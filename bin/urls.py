# -*- coding: utf-8 -*-
from handler import ping
from handler import login
from handler import item
from handler import prescription
from handler import train

urls = (
    # ping 接口
    ('/ping', ping.Ping),
    # 设备登录接口
    ('^/login$', login.LoginHandler),
    # 创建项目
    ('^/v1/item/create$', item.CreateHandler),
    # 修改项目
    ('^/v1/item/update$', item.UpdateHandler),
    # 获取项目详情
    ('^/v1/item/info$', item.InfoHandler),
    # 获取训练项目列表
    ('^/v1/item/list$', item.ListHandler),

    # 创建处方
    ('^/v1/prescription/create$', prescription.CreateHandler),
    # 修改处方
    ('^/v1/prescription/update$', prescription.UpdateHandler),
    # 处方详情
    ('^/v1/prescription/info$', prescription.InfoHandler),
    # 添加训练项目到处方
    ('^/v1/prescription/add_item$', prescription.AddItemHandler),
    # 删除处方中的训练项目
    ('^/v1/prescription/del_item$', prescription.DelItemHandler),
    # 修改一个处方里的一个训练项目
    ('^/v1/prescription/update_item$', prescription.UpdateItemHandler),

    # 创建训练
    ('^/v1/train/create$', train.CreateHandler),
    # 训练详情
    ('^/v1/train/info$', train.InfoHandler),
    # 训练记录列表
    ('^/v1/train/list$', train.ListHandler),
    # 完成训练
    ('^/v1/train/complete$', train.CompleteHandler),
)

