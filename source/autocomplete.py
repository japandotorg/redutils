import inspect
from fuzzywuzzy import process
from typing import Any, Callable, Iterable, List, Tuple, Optional

import discord
from redbot.core.bot import Red
from redbot.core import commands


class PromptSelect(discord.ui.Select):
    def __init__(self, parent: "PromptView", matches: List[Tuple[int, str]]) -> None:
        super().__init__(
            placeholder="Select an option below...",
            options=[
                discord.SelectOption(
                    label=str(match), description=f"{probability}% chance."
                )
                for match, probability in matches
            ],
        )
        self.parent: PromptView = parent

    async def callback(self, interaction: discord.Interaction[Red], /) -> None:
        assert interaction.message is not None

        await interaction.response.defer(thinking=True)

        selected = self.values
        if not selected:
            return

        self.parent.item = selected[0]
        await interaction.delete_original_response()
        await interaction.message.delete()

        self.parent.stop()


class PromptView(discord.ui.View):
    def __init__(
        self,
        *,
        ctx: commands.Context,
        matches: List[Tuple[int, str]],
        param: inspect.Parameter,
        value: str,
    ) -> None:
        super().__init__()
        self.ctx: commands.Context = ctx
        self.matches: List[Tuple[int, str]] = matches
        self.param: inspect.Parameter = param
        self.value: str = value
        self.item: Optional[str] = None

    async def interaction_check(self, interaction: discord.Interaction[Red], /) -> bool:
        return interaction.user == self.ctx.author

    @property
    def embed(self) -> discord.Embed:
        embed: discord.Embed = discord.Embed(
            title="That's not quite right!",
        )

        if self.value is not None:
            embed.description = f"`{self.value}` is not a valid response to the option named `{self.param.name}`, you need to select one of the following options below."
        else:
            embed.description = f"You did not enter a value for the option named `{self.param.name}`, you need to select one of the following options below."

        return embed


class AutoComplete:
    def __init__(self, func: Callable[..., Any], param_name: str) -> None:
        self.callback: Callable[..., Any] = func
        self.param_name: str = param_name
        
    async def prompt_correct_input(
        self, ctx: commands.Context, param: inspect.Parameter, /, *, value: str, constricted: Iterable[Any]
    ) -> str:
        assert ctx.command is not None
        
        result = [(item, 0) for item in constricted]
            
        view = PromptView(ctx=ctx, matches=result, param=param, value=value) # type: ignore
        await ctx.send(embed=view.embed, view=view)
        await view.wait()
        
        if view.item is None:
            raise commands.CommandError("You took too long, you need to redo this command.")
        
        return view.item
