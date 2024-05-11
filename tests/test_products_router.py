'''

@router.get(
    path="/"
)
async def test_get_all_products_view(
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency),
        user: User = Depends(get_current_user)

):
    products = await crud.get_all_products(session, user.id)
    return products


@router.get(path="/{id}")
async def test_get_product(
        id: str,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await crud.get_product_by_id(
        session=session,
        id=id,
        owner_id=user.id
    )

    return product


@router.patch(path="/{id}")
async def test_update_product_view(
        id: str,
        product_schema: ProductUpdate,
        user: User = Depends(get_current_user),
        session: AsyncSession = Depends(db_helper.get_scoped_session_dependency)
):

    product = await crud.get_product_by_id(
        session=session,
        id=id,
        owner_id=user.id
    )
    product = await crud.update_product(
        session=session,
        product=product,
        product_update=product_schema
    )

    return product
'''
