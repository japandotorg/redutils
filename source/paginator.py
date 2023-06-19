from itertools import islice
from contextlib import suppress
from typing import NamedTuple, Optional, List, Iterable, Tuple, Any, Union

import discord
from redbot.core import commands


def get_chunks(iterable: Iterable[Any], size: int) -> Iterable[Tuple[Any, Any]]:
    it = iter(iterable)
    return iter(lambda: tuple(islice(it, size)), ())


class Page(NamedTuple):
    index: int
    content: str


class Pages:
    def __init__(
        self,
        pages: List,
    ) -> None:
        super().__init__()
        self.pages = pages
        self.cur_page = 1

    @property
    def current_page(self) -> Page:
        return Page(self.cur_page, self.pages[self.cur_page - 1])

    @property
    def next_page(self) -> Optional[Page]:
        if self.cur_page == self.total:
            return None

        self.cur_page += 1
        return self.current_page

    @property
    def previous_page(self) -> Optional[Page]:
        if self.cur_page == 1:
            return None

        self.cur_page -= 1
        return self.current_page

    @property
    def first_page(self) -> Page:
        self.cur_page = 1
        return self.current_page

    @property
    def last_page(self) -> Page:
        self.cur_page = self.total
        return self.current_page

    @property
    def total(self) -> int:
        return len(self.pages)


class RedPaginator:
    def __init__(
        self,
        ctx: commands.Context,
        *,
        per_page: int = 10,
        timeout: float = 60.0,
        title: Optional[str] = None,
        show_page_count: bool = True,
    ):
        super().__init__()
        self.ctx = ctx
        self.per_page = per_page
        self.timeout = timeout
        self.title = title
        self.show_page_count = show_page_count

        self.lines: List = []
        self.pages: Optional[Pages] = None

    def add_lines(self, line: str, sep: str = "\n") -> None:
        self.lines.append(f"{line}{sep}")

    @property
    def embed(
        self, color: Union[int, discord.Color] = discord.Color.dark_embed()
    ) -> discord.Embed:
        page: Page = self.pages.current_page  # type: ignore

        em: discord.Embed = discord.Embed(color=color)
        if self.title:
            em.title = self.title

        em.description = page.content

        if self.show_page_count:
            em.set_footer(text=f"Page {page.index} of {self.pages.total}")  # type: ignore

        return em

    async def start(self):
        _pages = []
        for page in get_chunks(self.lines, self.per_page):
            _pages.append("".join(page))

        self.pages = Pages(_pages)

        if not self.pages.total > 1:
            return await self.ctx.send(embed=self.embed)

        view = PaginatorView(
            self.ctx,
            pages=self.pages,
            embed=self.embed,
            timeout=self.timeout,
            show_page_count=self.show_page_count,
        )

        view.message = await self.ctx.send(embed=self.embed, view=view)


class PaginatorView(discord.ui.View):
    message: discord.Message

    def __init__(
        self,
        ctx: commands.Context,
        pages: Pages,
        embed: discord.Embed,
        timeout: float,
        show_page_count: bool,
    ) -> None:
        super().__init__(timeout=timeout)

        self.ctx = ctx
        self.pages = pages
        self.embed = embed
        self.show_page_count = show_page_count

        if self.pages.cur_page == 1:
            self.children[0].disabled = True  # type: ignore
            self.children[1].disabled = True  # type: ignore

    def _lock(self) -> None:
        if self.pages.cur_page == self.pages.total:
            self.children[0].disabled = False  # type: ignore
            self.children[1].disabled = False  # type: ignore

            self.children[2].disabled = True  # type: ignore
            self.children[3].disabled = True  # type: ignore

        elif self.pages.cur_page == 1:
            self.children[0].disabled = True  # type: ignore
            self.children[1].disabled = True  # type: ignore

            self.children[2].disabled = False  # type: ignore
            self.children[3].disabled = False  # type: ignore

        elif 1 < self.pages.cur_page < self.pages.total:
            for child in self.children:
                child.disabled = False  # type: ignore

    def _update_embed(self, page: Page, /) -> None:
        if self.show_page_count:
            self.embed.set_footer(text=f"Page {page.index} of {self.pages.total}")

        self.embed.description = page.content

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id != self.ctx.author.id:
            await interaction.response.send_message(
                "Sorry, you can't use this interaction as it is not started by you.",
                ephemeral=True,
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for child in self.children:
            child.style, child.disabled = discord.ButtonStyle.grey, True  # type: ignore

        with suppress(discord.HTTPException):
            await self.message.edit(view=self)

    @discord.ui.button(
        style=discord.ButtonStyle.green,
        custom_id="first",
        emoji="\N{BLACK LEFT-POINTING DOUBLE TRIANGLE}\N{VARIATION SELECTOR-16}",
    )
    async def _first(
        self, interaction: discord.Interaction, button: discord.ui.Button, /
    ):
        await interaction.response.defer()
        page = self.pages.first_page

        self._update_embed(page)
        self._lock()
        await interaction.message.edit(embed=self.embed, view=self)  # type: ignore

    @discord.ui.button(
        style=discord.ButtonStyle.green,
        custom_id="previous",
        emoji="\N{BLACK LEFT-POINTING TRIANGLE}\N{VARIATION SELECTOR-16}",
    )
    async def _previous(
        self, interaction: discord.Interaction, button: discord.ui.Button, /
    ):
        await interaction.response.defer()
        page = self.pages.previous_page

        self._update_embed(page)  # type: ignore
        self._lock()
        await interaction.message.edit(embed=self.embed, view=self)  # type: ignore

    @discord.ui.button(
        style=discord.ButtonStyle.green,
        custom_id="next",
        emoji="\N{BLACK RIGHTWARDS ARROW}\N{VARIATION SELECTOR-16}",
    )
    async def _next(
        self, interaction: discord.Interaction, button: discord.ui.Button, /
    ):
        await interaction.response.defer()
        page = self.pages.next_page

        self._update_embed(page)  # type: ignore
        self._lock()
        await interaction.message.edit(embed=self.embed, view=self)  # type: ignore

    @discord.ui.button(
        style=discord.ButtonStyle.green,
        custom_id="last",
        emoji="\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE}\N{VARIATION SELECTOR-16}",
    )
    async def _last(
        self, interaction: discord.Interaction, button: discord.ui.Button, /
    ):
        await interaction.response.defer()
        page = self.pages.last_page

        self._update_embed(page)
        self._lock()
        await interaction.message.edit(embed=self.embed, view=self)  # type: ignore
