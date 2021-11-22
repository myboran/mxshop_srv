import json

import grpc
from google.protobuf import empty_pb2
from loguru import logger
from peewee import DoesNotExist

from goods_srv.proto import goods_pb2, goods_pb2_grpc
from goods_srv.model.models import Goods, Category, Brands


class GoodsServicer(goods_pb2_grpc.GoodsServicer):

    def convert_model_to_message(self, goods):
        info_rsp = goods_pb2.GoodsInfoResponse()

        info_rsp.id = goods.id
        info_rsp.categoryId = goods.category_id
        info_rsp.name = goods.name
        info_rsp.goodsSn = goods.goods_sn
        info_rsp.clickNum = goods.click_num
        info_rsp.soldNum = goods.sold_num
        info_rsp.favNum = goods.fav_num
        info_rsp.marketPrice = goods.market_price
        info_rsp.shopPrice = goods.shop_price
        info_rsp.goodsBrief = goods.goods_brief
        info_rsp.shipFree = goods.ship_free

        info_rsp.goodsFrontImage = goods.goods_front_image
        info_rsp.isNew = goods.is_new
        info_rsp.isHot = goods.is_hot
        info_rsp.onSale = goods.on_sale

        info_rsp.descImages.extend(goods.desc_images)
        info_rsp.images.extend(goods.desc_images)

        info_rsp.category.id = goods.category.id
        info_rsp.category.name = goods.category.name

        info_rsp.brand.id = goods.brand.id
        info_rsp.brand.name = goods.brand.name
        info_rsp.brand.logo = goods.brand.logo

        return info_rsp

    @logger.catch
    def GoodsList(self, request, context):
        # 商品列表页
        rsp = goods_pb2.GoodsListResponse()
        goods = Goods.select()
        if request.keyWords:
            goods = goods.where(Goods.name.contains(request.keyWords))
        if request.isHot:
            goods = goods.filter(Goods.is_hot == True)
        if request.isNew:
            goods = goods.filter(Goods.is_new == True)
        if request.priceMin:
            goods = goods.filter(Goods.shop_price >= request.priceMin)
        if request.priceMax:
            goods = goods.filter(Goods.shop_price <= request.priceMax)
        if request.brand:
            goods = goods.filter(Goods.brand_id == request.brand)
        if request.topCategory:
            try:
                ids = []
                category = Category.get(Category.id == request.topCategory)
                level = category.level

                if level == 1:
                    c2 = Category.alias()
                    categories = Category.select().where(Category.parent_category_id.in_(
                        c2.select(c2.id).where(c2.parent_category_id == request.topCategory)))
                    for category in categories:
                        ids.append(category.id)
                elif level == 2:
                    categories = Category.select().where(Category.parent_category_id == request.topCategory)
                    for category in categories:
                        ids.append(category.id)
                elif level == 3:
                    ids.append(request.topCategory)

                goods = goods.where(Goods.category_id.in_(ids))
            except Exception as e:
                pass

        # 分页 limit offset
        start = 0
        per_page_num = 10
        if request.pagePerNums:
            per_page_num = request.pagePerNums
        if request.pages:
            start = per_page_num * (request.pages - 1)

        rsp.total = goods.count()

        goods = goods.limit(per_page_num).offset(start)

        for good in goods:
            rsp.data.append(self.convert_model_to_message(good))
        return rsp

    @logger.catch
    def BatchGetGoods(self, request, context):
        # 批量获取商品详情， 订单新建的时候可以使用
        rsp = goods_pb2.GoodsListResponse()
        goods = Goods.select().where(Goods.id.in_(list(request.id)))

        rsp.total = goods.count()

        for good in goods:
            rsp.data.append(self.convert_model_to_message(good))
        return rsp

    @logger.catch
    def DeleteGoods(self, request: goods_pb2.DeleteGoodsInfo, context):
        # 删除商品
        try:
            goods = Goods.get(Goods.id==request.id)
            goods.delete_instance()
            return empty_pb2.Empty()
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("记录不存在")
            return empty_pb2.Empty()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return empty_pb2.Empty()

    @logger.catch
    def GetGoodsDetail(self, request: goods_pb2.GoodInfoRequest, context):
        try:
            goods = Goods.get(Goods.id == request.id)

            goods.click_num += 1
            goods.save()

            return self.convert_model_to_message(goods)
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("记录不存在")
            return goods_pb2.GoodsInfoResponse()

    @logger.catch
    def CreateGoods(self, request, context):
        try:
            category = Category.get(Category.id==request.categoryId)
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("库存设置失败")
            return goods_pb2.GoodsInfoResponse()

        try:
            brand = Brands.get(Brands.id==request.brandId)
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("品牌不存在")
            return goods_pb2.GoodsInfoResponse()

        goods = Goods()
        goods.brand = brand
        goods.category = category
        goods.name = request.name
        goods.goods_sn = request.goodsSn
        goods.market_price = request.marketPrice
        goods.shop_price = request.shopPrice
        goods.goods_brief = request.goodsBrief
        goods.ship_free = request.shipFree
        goods.images = list(request.images)
        goods.desc_images = list(request.descImages)
        goods.goods_front_image = request.goodsFrontImage
        goods.is_new = request.isNew
        goods.is_hot = request.isHot
        goods.on_sale = request.onSale

        goods.save()
        # TODO 此处完善库存的设置 - 分布式事务
        return self.convert_model_to_message(goods)

    @logger.catch
    def UpdateGoods(self, request, context):
        try:
            category = Category.get(Category.id == request.categoryId)
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("商品分类不存在")
            return goods_pb2.GoodsInfoResponse()

        try:
            brand = Brands.get(Brands.id == request.brandId)
        except Exception as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("品牌不存在")
            return goods_pb2.GoodsInfoResponse()

        try:
            goods = Goods.get(Goods.id==request.id)
        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("商品不存在")
            return goods_pb2.GoodsInfoResponse()

        goods.brand = brand
        goods.category = category
        goods.name = request.name
        goods.goods_sn = request.goodsSn
        goods.market_price = request.marketPrice
        goods.shop_price = request.shopPrice
        goods.goods_brief = request.goodsBrief
        goods.ship_free = request.shipFree
        goods.images = list(request.images)
        goods.desc_images = list(request.descImages)
        goods.goods_front_image = request.goodsFrontImage
        goods.is_new = request.isNew
        goods.is_hot = request.isHot
        goods.on_sale = request.onSale

        goods.save()

        # TODO 此处完善库存的设置 - 分布式事务
        return self.convert_model_to_message(goods)

    def category_model_to_dict(self, category):
        re = {}

        re["id"] = category.id
        re["name"] = category.name
        re["level"] = category.level
        re["parent"] = category.parent_category_id
        re["is_tab"] = category.is_tab

        return re

    @logger.catch
    def GetAllCategorysList(self, request, context):
        # 商品分类
        """
            [{
                "name": "xxx",
                "id": "xxx",
                "sub_category": [
                    {
                        "name": "xxx",
                        "id": "xxx",
                        "sub_category": [
                        ]
                    }
                ]
            },{},{},{}]
        """
        level1 = []
        level2 = []
        level3 = []

        category_list_rsp = goods_pb2.CategoryListResponse()
        category_list_rsp.total = Category.select().count()

        for category in Category.select():

            category_rsp = goods_pb2.CategoryInfoResponse()

            category_rsp.id = category.id
            category_rsp.name = category.name
            if category.parent_category_id:
                category_rsp.parentCategory = category.parent_category_id
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab

            category_list_rsp.data.append(category_rsp)

            if category.level == 1:
                level1.append(self.category_model_to_dict(category))
            elif category.level == 2:
                level2.append(self.category_model_to_dict(category))
            elif category.level == 3:
                level3.append(self.category_model_to_dict(category))

        # 开始整理数据
        for data3 in level3:
            for data2 in level2:
                if data3["parent"] == data2["id"]:
                    if "sub_category" not in data2:
                        data2["sub_category"] = [data3]
                    else:
                        data2["sub_category"].append(data3)

        for data2 in level2:
            for data1 in level1:
                if data2["parent"] == data1["id"]:
                    if "sub_category" not in data1:
                        data1["sub_category"] = [data2]
                    else:
                        data1["sub_category"].append(data2)

        category_list_rsp.jsonData = json.dumps(level1).encode()
        return category_list_rsp

    @logger.catch
    def GetSubCategory(self, request: goods_pb2.CategoryListRequest, context):
        category_list_rsp = goods_pb2.SubCategoryListResponse()

        try:
            category_info = Category.get(Category.id == request.id)
            category_list_rsp.info.id = category_info.id
            category_list_rsp.info.name = category_info.name
            category_list_rsp.info.level = category_info.level
            category_list_rsp.info.isTab = category_info.is_tab
            if category_info.parent_category:
                category_list_rsp.info.parentCategory = category_info.parent_category_id
        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('记录不存在')
            return goods_pb2.SubCategoryListResponse()

        categorys = Category.select().where(Category.parent_category == request.id)
        category_list_rsp.total = categorys.count()
        for category in categorys:
            category_rsp = goods_pb2.CategoryInfoResponse()
            category_rsp.id = category.id
            category_rsp.name = category.name
            if category_info.parent_category:
                category_rsp.parentCategory = category_info.parent_category_id
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab

            category_list_rsp.subCategorys.append(category_rsp)

        return category_list_rsp

    @logger.catch
    def CreateCategory(self, request: goods_pb2.CategoryInfoRequest, context):
        try:
            category = Category()
            category.name = request.name
            if request.level != 1:
                category.parent_category = request.parentCategory
            category.level = request.level
            category.is_tab = request.isTab
            category.save()

            category_rsp = goods_pb2.CategoryInfoResponse()
            category_rsp.id = category.id
            category_rsp.name = category.name
            if category.parent_category:
                category_rsp.parentCategory = category.parent_category.id
            category_rsp.level = category.level
            category_rsp.isTab = category.is_tab
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('插入数据失败：' + str(e))
            return goods_pb2.CategoryInfoResponse()

        return category_rsp
