from abc import ABC
from datetime import datetime
from peewee import *

from playhouse.shortcuts import ReconnectMixin
from playhouse.pool import PooledMySQLDatabase
from playhouse.mysql_ext import JSONField


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


db = ReconnectMySQLDatabase("mxshop_srv_goods", host="120.78.84.24", port=3306, user="root", password="ACB123456acb!")


# 删除 物理删除 逻辑删除
class BaseModel(Model):
    is_deleted = BooleanField(default=False, verbose_name="是否删除")
    add_time = DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = DateTimeField(default=datetime.now, verbose_name="更新时间")

    def save(self, *args, **kwargs):
        # 判断这是一个新添加的数据还是更新的数据
        if self._pk is not None:
            # 这是一个新数据
            self.update_time = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def delete(cls, permanently=False):  # permanently表示是否永久删除
        if permanently:
            return super().delete()
        else:
            return super().update(is_deleted=True)

    def delete_instance(self, permanently=False, recursive=False, delete_nullable=False):
        if permanently:
            return self.delete(permanently).where(self._pk_expr()).execute()
        else:
            self.is_deleted = True
            self.save()

    @classmethod
    def select(cls, *fields):
        return super().select(*fields).where(cls.is_deleted == False)

    class Meta:
        database = db


class Category(BaseModel):
    name = CharField(max_length=20, verbose_name="名称")
    level = IntegerField(default=1, verbose_name="级别")
    is_tab = BooleanField(default=False, verbose_name="是否显示在首页tab")
    parent_category = ForeignKeyField("self", verbose_name="父类别", null=True)


class Brands(BaseModel):
    # 品牌
    name = CharField(max_length=50, index=True, unique=True, verbose_name="名称")
    logo = CharField(max_length=200, null=True, default="", verbose_name="图标")


class Goods(BaseModel):
    category = ForeignKeyField(Category, on_delete='CASCADE', verbose_name="商品类目")
    brand = ForeignKeyField(Brands, on_delete="CASCADE", verbose_name="品牌")
    on_sale = BooleanField(default=True, verbose_name="是否上架")
    goods_sn = CharField(max_length=50, default="", verbose_name="商品唯一货号")
    name = CharField(max_length=100, verbose_name="商品名")
    click_num = IntegerField(default=0, verbose_name="点击数")
    sold_num = IntegerField(default=0, verbose_name="商品销售量")
    fav_num = IntegerField(default=0, verbose_name="收藏数")  # 库存是电商中一个重要的环节
    market_price = FloatField(default=0, verbose_name="市场价格")
    shop_price = FloatField(default=0, verbose_name="本店价格")
    goods_brief = CharField(max_length=200, verbose_name="商品简短描述")
    ship_free = BooleanField(default=True, verbose_name="是否承担运费")
    images = JSONField(verbose_name="商品轮播图")
    desc_images = JSONField(verbose_name="详情页图片")
    goods_front_image = CharField(max_length=200, verbose_name="封面图")
    is_new = BooleanField(default=False, verbose_name="是否新品")
    is_hot = BooleanField(default=False, verbose_name="是否热销")


class GoodsCategoryBrand(BaseModel):
    # 品牌分类
    id = AutoField(primary_key=True, verbose_name="id")
    category = ForeignKeyField(Category, verbose_name="类别")
    brand = ForeignKeyField(Brands, verbose_name="品牌")

    class Meta:
        indexes = (
            # 联合主键
            (("category", "brand"), True),
        )


class Banner(BaseModel):
    """
    轮播的商品
    """
    image = CharField(max_length=200, default="", verbose_name="图片url")
    url = CharField(max_length=200, default="", verbose_name="访问url")
    index = IntegerField(default=0, verbose_name="轮播顺序")


if __name__ == '__main__':
    # # id1 = Category.get(Category.id==2)
    # # id1.delete_instance()
    # for c in Category.select():
    #     print(c.id, c.name)
    db.create_tables([Category, Goods, Brands, GoodsCategoryBrand, Banner])
