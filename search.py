from bilibili_api import search, sync

print(
    sync(
        search.search_by_type(
            "音乐",
            search_type=search.SearchObjectType.USER,
            order_type=search.OrderUser.FANS,
            order_sort=0,
        )
    )
)