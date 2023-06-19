import io
import re
import logging
from typing import List, Dict, Optional, Union, Any

import discord


def silence_debug_loggers(
    main_logger: logging.Logger, logger_level: int, *, logger_names: List[str]
) -> None:
    """
    A helper function that suppress debug logs for specified modules.

    .. versionadded:: 1.0

    Info
    ----------
    0: Critical
    1: Error
    2: Warning
    3: Info
    4: Debug
    5: Verbose
    6: Trace

    Parameters
    ----------
    main_logger: logging.Logger
        The bot/cog's main logger.
    logger_level: int
        The logging level.
    logger_names: List[str]
        The name of the loggers which are to be suppressed.

    Raises
    ----------
    ValueError
        If Invalid ``logger_level`` is provided.
    """
    level_map = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
        5: logging.DEBUG - 3,
        6: logging.DEBUG - 5,
    }
    if logger_level not in level_map:
        raise ValueError("Invalid logger level.")
    for logger_name in logger_names:
        logging.getLogger(logger_name).setLevel(level_map[logger_level])
        main_logger.warning(f"Silenced debug logger: {logger_name}.")


def write_to_discord_file(filename: str, content: str) -> discord.File:
    """
    A helper function to send a ``discord.File`` with text content.

    .. versionadded:: 1.0

    Parameters
    ----------
    filename: str
        The name of the file to be send.
    content: str
        The text to be uploaded to the file.

    Returns
    -------
    :class:`discord.File`
        The file to be send.
    """
    stream = io.BytesIO()
    stream.write(content.encode())
    stream.seek(0)
    return discord.File(stream, filename=filename)


def create_embeds(
    fmt_line: str,
    arguments: List[Dict],
    color: Optional[Union[int, discord.Color]] = None,
    per_page: Optional[int] = None,
) -> Optional[List[discord.Embed]]:
    """
    A helper function to create a list of embeds from a list of arguments.

    .. versionadded:: 1.0

    Examples
    ----------
    >>> create_embeds("Hello {name}!", [{"name": "Lemon"}, {"name": "Melon"}, ...], color=0x2f3136, per_page=10)

    Parameters
    ----------
    fmt_line: str
        The format line to use.
    arguments: List[Dict]
        The arguments to use.
    color: Optional[Union[int, discord.Color]]
        The color to use for the embeds.
    per_page: Optional[int]
        The number of arguments to put in each embed.

    Returns:
    ----------
    :class:`Optional[List[discord.Embed]]`
        A list of embeds or ``NoneType`` if no arguments.
    """
    if not arguments:
        return None

    embeds: List[discord.Embed] = []
    max_desc_length: int = 4096
    append_list: bool = False
    embed: discord.Embed = discord.Embed(
        title="",
        description="",
        color=color,
    )

    for i, arg in enumerate(arguments):
        if len(embed.description) + len(fmt_line.format(**arg)) + 1 > max_desc_length:  # type: ignore
            embeds.append(embed)
            embed: discord.Embed = discord.Embed(
                title="",
                description="",
                color=color,
            )

        elif per_page is not None and 1 > 0 and i % per_page == 0:
            embeds.append(embed)
            embed: discord.Embed = discord.Embed(
                title="",
                description="",
                color=color,
            )

        embed.description += fmt_line.format(**arg) + "\n"  # type: ignore
        if i == len(arguments) - 1:
            append_list = True

    if append_list:
        embeds.append(embed)

    return embeds


def modify_embeds(
    embeds: List[discord.Embed],
    title_kwargs: Optional[Dict] = None,
    author_kwargs: Optional[Dict] = None,
    footer_kwargs: Optional[Dict] = None,
    thumbnail_image_url: Optional[Union[str, List[str]]] = None,
    image_url: Optional[Union[str, List[str]]] = None,
    show_page_number: Optional[bool] = False,
) -> List[discord.Embed]:
    """
    A helper function to modify a list of embeds.

    .. versionadded:: 1.0

    Examples
    ----------
    >>> modify_embeds(
    ...     embeds,
    ...     title_kwargs={"name", "Lemon"},
    ...     author_kwargs={"name", "Melon", "icon_url": "https://example.com/icon.png"},
    ...     footer_kwargs={"text": "Red"},
    ...     thumnail_image_url="https://example.com/thumbnail.png",
    ...     image_url="https://example.com/image.png",
    ...     show_page_number=True,
    ... )

    Parameters
    ----------
    embeds: List[discord.Embed]
        The embeds to modify.
    title_kwargs: Optional[Dict]
        The title kwargs to use.
    author_kwargs: Optional[Dict]
        The author kwargs to use.
    footer_kwargs: Optional[Dict]
        The footer kwargs to use.
    thumbnail_image_url: Optional[union[str, List[str]]]
        The thumbnail image URL to use.
    image_url: Optional[union[str, List[str]]]
        The image URL to use.
    show_page_number: Optional[bool]
        Whether to show the page_number.

    Returns
    ----------
    :class:`List[discord.Embed]`
        The modified embeds.
    """
    for i, em in enumerate(embeds):
        if title_kwargs:
            em.title = title_kwargs.get("title")
            em.color = title_kwargs.get("color")
            em.url = title_kwargs.get("url")
        if author_kwargs:
            em.set_author(**author_kwargs)
        if footer_kwargs:
            em.set_footer(**footer_kwargs)
        if show_page_number:
            if em.footer.text:
                em.set_footer(text=f"{em.footer.text} | Page {i + 1}/{len(embeds)}")
            else:
                em.set_footer(text=f"Page {i + 1}/{len(embeds)}")
        if thumbnail_image_url:
            if isinstance(thumbnail_image_url, list):
                em.set_thumbnail(url=thumbnail_image_url[i])
            else:
                em.set_thumbnail(url=thumbnail_image_url)
        if image_url:
            if isinstance(image_url, list):
                em.set_image(url=image_url[i])
            else:
                em.set_image(url=image_url)

    return embeds


def group_items_by(items: List[Any], key_path: List[str]) -> List[List[Any]]:
    """
    A helper function to group items by a key path.

    .. versionadded:: 1.0

    Examples
    ----------
    >>> from enum import Enum
    >>> class Color(Enum):
    ...    RED   = 1
    ...    GREEN = 2
    ...    BLUE  = 3
    ...
    >>> items = [Color.RED, Color.GREEN, Color.BLUE, Color.RED]
    >>> group_items_by(items, ["value"])
    [[<Color.RED: 1>, <Color.RED: 1>], [<Color.GREEN: 2>], [<Color.BLUE: 3>]]

    Parameters
    ----------
    items: List[Any]
        The items to group.
    key_path: List[str]
        The key path to use, where each element is an attribute name.

    Returns
    ----------
    :class:`List[List[Any]]`
        The grouped items.
    """
    if not key_path:
        return [items]

    def get_attr(obj, path):
        for attr in path:
            obj = getattr(obj, attr)
        return obj

    key = key_path[0]
    groups = {}
    for item in items:
        value = get_attr(item, key.split("."))
        if value not in groups:
            groups[value] = []
            groups[value].append(item)

    sub_key_path = key_path[1:]
    sub_groups = []
    for group in groups.values():
        sub_groups.extend(group_items_by(group, sub_key_path))

    return sub_groups


def parse_raw_mentions(text: str) -> List[int]:
    """
    A helper function that parses mentions from a sing as an array of
    :class:`~discord.User` IDs matched with the syntax of ``<@user_id>``
    or ``<@!user_id>``.

    .. versionadded:: 1.0

    .. note::

        This does not include role or channel mentions.
        See :func:`parse_raw_role_mentions` and
        :func:`parse_raw_channel_mentions` for those.

    Parameters
    ----------
    text: str
        The text to parse mentions from.

    Returns
    ----------
    :class:`List[int]`
        A list of user IDs that were mentioned.
    """
    return [int(x) for x in re.findall(r"<@!?(\d{15,20})>", text)]


def parse_raw_role_mentions(text: str) -> List[int]:
    """A helper function that parses mentions from a string as an array of
    :class:`~discord.Role` IDs matched with the syntax of ``<@&role_id>``.

    .. versionadded:: 1.0

    Parameters
    ----------
    text: str
        The text to parse mentions from.

    Returns
    -------
    :class:`List[int]`
        A list of role IDs that were mentioned.
    """
    return [int(x) for x in re.findall(r"<@&(\d{15,20})>", text)]


def parse_raw_channel_mentions(text: str) -> List[int]:
    """
    A helper function that parses mentions from a string as an array of
    :class:`~discord.abc.GuildChannel` IDs matched with the syntax of
    ``<#channel_id>``.

    .. versionadded:: 1.0

    Parameters
    ----------
    text: str
        The text to parse mentions from.

    Returns
    ----------
    :class:`List[int]`
        A list of channel IDs that were mentioned.
    """
    return [int(x) for x in re.findall(r"<#(\d{15,20})>", text)]


async def get_or_fetch(
    obj: Any, attr: str, id: int, *, default: Any = discord.utils.MISSING
) -> Any:
    """|coro|
    
    Attempts to get an attribute from the object in cache. If it fails, 
    it will attempt to fetch it. If the fetch also fails, an error will 
    be raised.
    
    Parameters
    ----------
    obj: Any
        The object to use the get or fetch methods in.
    attr: str
        The attribute to get or fetch. Note the object must have both a ``get_`` and ``fetch_`` method for this attribute.
    id: int
        The ID of the object
    default: Any
        The default value to return if the object is not found, instead of raising an error.
    
    Returns
    ----------
    Any
        The object found or the default value.
        
    Raises
    ----------
    :exc:`AttributeError`
        The object is missing a ``get_`` or ``fetch_`` method
    :exc:`NotFound`
        Invalid ID for the object
    :exc:`HTTPException`
        An error occurred fetching the object
    :exc:`Forbidden`
        You do not have permission to fetch the object
      
    Examples  
    ----------
    Getting a guild from a guild ID: ::

        guild = await get_or_fetch(client, 'guild', guild_id)

    Getting a channel from the guild. If the channel is not found, return None: ::

        channel = await get_or_fetch(guild, 'channel', channel_id, default=None)
    """
    getter = getattr(obj, f"get_{attr}")(id)
    if getter is None:
        try:
            getter = await getattr(obj, f"fetch_{attr}")(id)
        except AttributeError:
            getter = await getattr(obj, f"_fetch_{attr}")(id)
            if getter is None:
                raise ValueError(f"Could not find {attr} with id {id} on {obj}")
        except (discord.HTTPException, ValueError):
            if default is not discord.utils.MISSING:
                return default
            else:
                raise
    return getter
            
