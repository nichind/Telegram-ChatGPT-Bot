

def formatter(str, user, language, lore, model, custom_lore) -> str:
    return str.format(
        username=user.username,
        language=language,
        lore=lore,
        model=model,
        custom_lore=custom_lore,
        user_id=user.id
    )
