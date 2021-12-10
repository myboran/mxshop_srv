from datetime import datetime

from peewee import *
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin

from inventory_srv.settings import settings


class ReconnectMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass

# db = ReconnectMySQLDatabase("mxshop_inventory_srv", host="120.78.84.24",  port=3306, user="root", password="ACB123456acb!")

class BaseModel(Model):
    add_time = DateTimeField(default=datetime.now, verbose_name="添加时间")
    is_deleted = BooleanField(default=False, verbose_name="是否删除")
    update_time = DateTimeField(verbose_name="更新时间", default=datetime.now)

    def save(self, *args, **kwargs):
        #判断这是一个新添加的数据还是更新的数据
        if self._pk is not None:
            #这是一个新数据
            self.update_time = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def delete(cls, permanently=False): #permanently表示是否永久删除
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
        return super().select(*fields).where(cls.is_deleted==False)

    class Meta:
        database = settings.DB


class Inventory(BaseModel):
    #商品的库存表
    # stock = PrimaryKeyField(Stock)
    goods = IntegerField(verbose_name="商品id", unique=True)
    stocks = IntegerField(verbose_name="库存数量", default=0)
    version = IntegerField(verbose_name="版本号", default=0) #分布式锁的乐观锁

class InventoryNew(BaseModel):
    #商品的库存表
    # stock = PrimaryKeyField(Stock)
    goods = IntegerField(verbose_name="商品id", unique=True)
    stocks = IntegerField(verbose_name="库存数量", default=0)
    version = IntegerField(verbose_name="版本号", default=0) #分布式锁的乐观锁
    freeze = IntegerField(verbose_name="冻结数量", default=0)


# class A(BaseModel):
#
#     num = IntegerField()
#     name = CharField()
#     age = IntegerField()
#
# class B(BaseModel):
#     F = ForeignKeyField(A.id)
#     name = CharField()
#
#
# class C(BaseModel):
#     F = ForeignKeyField(A.age)
#     name = CharField()

if __name__ == "__main__":
    # pass
    # settings.DB.create_tables([B,C])
    #
    # # b = B().select(B.F==2)
    # # a = b[0]
    # # print(b)
    # # print(a)
    # c = C.get(C.F==1)
    # print(c.F.name)

    for i in range(1, 8):
        try:
            inv = Inventory.get(Inventory.goods == i)
        except DoesNotExist as e:
            inv = Inventory(goods=i, stocks=7)

        inv.save()