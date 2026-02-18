"""Helper for handling text_override in element style APIs."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sqlalchemy.styles import TextOverrideStyle


async def apply_text_override(
    session: AsyncSession,
    row: Any,
    text_override_value: dict | None,
) -> None:
    """
    Apply text_override to a style row.
    - If text_override_value is None: clear the override (delete if exists, set FK to None).
    - If dict: create or update TextOverrideStyle, set row.text_override_style_id.
    """
    if text_override_value is None:
        if row.text_override_style_id is not None:
            existing = await session.get(TextOverrideStyle, row.text_override_style_id)
            if existing:
                await session.delete(existing)
            row.text_override_style_id = None
        return

    # Build update dict
    data = (
        text_override_value
        if isinstance(text_override_value, dict)
        else text_override_value.model_dump(exclude_unset=True)
    )

    if row.text_override_style_id is not None:
        to_row = await session.get(TextOverrideStyle, row.text_override_style_id)
        if to_row is None:
            to_row = TextOverrideStyle()
            session.add(to_row)
            await session.flush()
            row.text_override_style_id = to_row.id
    else:
        to_row = TextOverrideStyle()
        session.add(to_row)
        await session.flush()
        row.text_override_style_id = to_row.id

    # Update fields present in data (empty dict = create with defaults only)
    valid_keys = {f for f in data if hasattr(to_row, f)}
    for key in valid_keys:
        setattr(to_row, key, data[key])
