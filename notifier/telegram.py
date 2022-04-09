import pickle
from enum import Enum
from http import HTTPStatus
from http.client import HTTPException
from os import makedirs
from os.path import join
from pathlib import Path
from typing import Tuple

import requests


class API(Enum):
    GET_UPDATES = 'getUpdates'
    SEND_MESSAGE = 'sendMessage'


DATA_PATH = Path(join(Path(__file__).parent, 'data', 'chat_ids.pkl'))


class TelegramNotifier(object):

    def __init__(self, api_token: str, telegram_url: str):
        def query_constructor(query: API) -> str:
            return f'{telegram_url}/bot{api_token}/{query.value}'

        self._query_constructor = query_constructor
        self._chat_ids = set()
        self._synchronize()

    def _synchronize(self) -> None:
        synchronized_ids = self._chat_ids
        if DATA_PATH.exists():
            with open(DATA_PATH, 'rb') as ids_file:
                saved_ids = pickle.load(ids_file)
            synchronized_ids = synchronized_ids.union(saved_ids)

        makedirs(DATA_PATH.parent, exist_ok=True)
        with open(DATA_PATH, 'wb') as ids_file:
            pickle.dump(synchronized_ids, ids_file, pickle.HIGHEST_PROTOCOL)

        self._chat_ids = synchronized_ids

    def notify(self, message: str) -> None:
        self._update_chat_ids()

        query = self._query_constructor(API.SEND_MESSAGE)
        for chat_id in self._chat_ids:
            data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
            try:
                requests.get(query, data=data, timeout=10)
            except HTTPException:
                pass

    def _fetch_all_available_updates(self) -> Tuple[dict, ...]:
        updates = []
        query = self._query_constructor(API.GET_UPDATES)

        curr_offset = 0
        query_successful = True
        while query_successful:
            try:
                data = {"offset": curr_offset}
                response = requests.get(query, data=data, timeout=10)

                if response.status_code != HTTPStatus.OK:
                    query_successful = False
                    continue

                new_updates = response.json().get('result', [])
                if not len(new_updates):
                    query_successful = False
                    continue

                new_update_ids = {new_update.get('update_id', 0) for new_update in new_updates}
                curr_offset = max(new_update_ids) + 1
                updates.extend(new_updates)

            except HTTPException:
                query_successful = False

        return tuple(updates)

    def _update_chat_ids(self) -> None:
        updates = self._fetch_all_available_updates()
        messages = [update['message'] for update in updates if 'message' in update]
        new_chat_ids = {message['chat']['id'] for message in messages}

        self._chat_ids.update(new_chat_ids)
        self._synchronize()
