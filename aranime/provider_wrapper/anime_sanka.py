from time import sleep
from rich.console import Console
from .base_provider import Provider
from ..anime_interface import Anime, Episode, Server
from ..utils import wait, die, debug
from pdb import set_trace
from ..scrapers.anime_sanka_scraper import (
    get_search_results_link,
    get_all_episodes_server_link,
)

console = Console()


class AnimeSanka(Provider):
    def __init__(self, anime: Anime) -> None:
        super().__init__(anime)

    @classmethod
    def _search_anime(cls, search_term: str, show_episode_count=True) -> list["Anime"]:
        result = get_search_results_link(search_term)
        result = [Anime(**i) for i in result]

        if show_episode_count:
            for i, anime in enumerate(result):
                with console.status(
                    f"getting episode count for {cls.__name__}/{search_term}: [bold]{i+1}[/]/{len(result)}"
                ):
                    episodes = get_all_episodes_server_link(anime_link=anime.link)
                    anime.episode_count = len(episodes)

        if len(result) == 0:
            console.log(f'anime "{search_term}" not found in anime-sanka')
            return []
        result = sorted(result, key=lambda x: abs(len(x.name) - len(search_term)))
        return result

    def _request_episodes(self) -> list["Episode"]:
        episode_info = get_all_episodes_server_link(self.anime.link)
        episodes: list[Episode] = []
        for number, server_links in episode_info:
            servers = [
                Server(link=server_link)
                for server_link in server_links
                if Server.is_downloadable(server_link)
            ]
            episode = Episode(provider=self, number=number, servers=servers)
            for server in servers:
                server.episode = episode
            episodes.append(episode)

        return episodes
