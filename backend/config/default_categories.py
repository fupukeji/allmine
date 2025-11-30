"""
默认资产分类模板
按照日常人们的资产分布设计的一级和二级分类体系
"""

DEFAULT_CATEGORIES = [
    {
        'name': '固定资产',
        'color': '#1890ff',
        'icon': 'home',
        'description': '房产、车辆等长期持有的实物资产',
        'sort_order': 1,
        'children': [
            {'name': '房产', 'color': '#1890ff', 'icon': 'home', 'description': '住宅、商铺、写字楼等', 'sort_order': 1},
            {'name': '车辆', 'color': '#13c2c2', 'icon': 'car', 'description': '汽车、摩托车等交通工具', 'sort_order': 2},
            {'name': '设备', 'color': '#2f54eb', 'icon': 'laptop', 'description': '电脑、手机等电子设备', 'sort_order': 3},
            {'name': '家具家电', 'color': '#722ed1', 'icon': 'appstore', 'description': '家具、家电等生活用品', 'sort_order': 4},
        ]
    },
    {
        'name': '金融资产',
        'color': '#52c41a',
        'icon': 'dollar',
        'description': '现金、存款、理财等流动金融资产',
        'sort_order': 2,
        'children': [
            {'name': '银行存款', 'color': '#52c41a', 'icon': 'bank', 'description': '活期、定期存款', 'sort_order': 1},
            {'name': '理财产品', 'color': '#73d13d', 'icon': 'fund', 'description': '银行理财、基金等', 'sort_order': 2},
            {'name': '股票', 'color': '#95de64', 'icon': 'stock', 'description': 'A股、港股、美股等', 'sort_order': 3},
            {'name': '债券', 'color': '#b7eb8f', 'icon': 'account-book', 'description': '国债、企业债等', 'sort_order': 4},
            {'name': '基金', 'color': '#d9f7be', 'icon': 'pie-chart', 'description': '公募基金、私募基金等', 'sort_order': 5},
            {'name': '保险', 'color': '#389e0d', 'icon': 'safety', 'description': '寿险、年金险等有现金价值的保险', 'sort_order': 6},
        ]
    },
    {
        'name': '投资资产',
        'color': '#faad14',
        'icon': 'rise',
        'description': '股权、债权等投资性资产',
        'sort_order': 3,
        'children': [
            {'name': '股权投资', 'color': '#faad14', 'icon': 'shop', 'description': '公司股权、合伙份额等', 'sort_order': 1},
            {'name': '债权投资', 'color': '#ffc53d', 'icon': 'file-text', 'description': '借款、债权等', 'sort_order': 2},
            {'name': '信托', 'color': '#ffd666', 'icon': 'safety-certificate', 'description': '家族信托、资金信托等', 'sort_order': 3},
            {'name': '私募股权', 'color': '#ffe58f', 'icon': 'cluster', 'description': 'PE、VC等私募股权投资', 'sort_order': 4},
        ]
    },
    {
        'name': '无形资产',
        'color': '#f5222d',
        'icon': 'bulb',
        'description': '知识产权、品牌等无形资产',
        'sort_order': 4,
        'children': [
            {'name': '知识产权', 'color': '#f5222d', 'icon': 'copyright', 'description': '专利、商标、著作权等', 'sort_order': 1},
            {'name': '域名', 'color': '#ff4d4f', 'icon': 'global', 'description': '互联网域名', 'sort_order': 2},
            {'name': '软件著作权', 'color': '#ff7875', 'icon': 'code', 'description': '软件产品著作权', 'sort_order': 3},
            {'name': '品牌价值', 'color': '#ffa39e', 'icon': 'crown', 'description': '商业品牌、商誉等', 'sort_order': 4},
        ]
    },
    {
        'name': '教育投资',
        'color': '#722ed1',
        'icon': 'read',
        'description': '教育培训、技能提升等人力资本投资',
        'sort_order': 5,
        'children': [
            {'name': '学历教育', 'color': '#722ed1', 'icon': 'book', 'description': '大学、研究生等学历教育', 'sort_order': 1},
            {'name': '职业培训', 'color': '#9254de', 'icon': 'solution', 'description': '职业技能培训、认证考试等', 'sort_order': 2},
            {'name': '兴趣爱好', 'color': '#b37feb', 'icon': 'heart', 'description': '音乐、美术、运动等培训', 'sort_order': 3},
            {'name': '子女教育', 'color': '#d3adf7', 'icon': 'team', 'description': '子女教育投资', 'sort_order': 4},
        ]
    },
    {
        'name': '收藏品',
        'color': '#fa8c16',
        'icon': 'gift',
        'description': '艺术品、古董等收藏投资',
        'sort_order': 6,
        'children': [
            {'name': '艺术品', 'color': '#fa8c16', 'icon': 'picture', 'description': '字画、雕塑等艺术品', 'sort_order': 1},
            {'name': '古董', 'color': '#ffa940', 'icon': 'golden', 'description': '文物、古董等', 'sort_order': 2},
            {'name': '珠宝', 'color': '#ffc069', 'icon': 'skin', 'description': '钻石、翡翠等珠宝首饰', 'sort_order': 3},
            {'name': '贵金属', 'color': '#ffd591', 'icon': 'gold', 'description': '黄金、白银等实物贵金属', 'sort_order': 4},
            {'name': '其他收藏', 'color': '#ffe7ba', 'icon': 'container', 'description': '邮票、钱币等其他收藏品', 'sort_order': 5},
        ]
    },
    {
        'name': '数字资产',
        'color': '#13c2c2',
        'icon': 'link',
        'description': '加密货币、NFT等数字资产',
        'sort_order': 7,
        'children': [
            {'name': '加密货币', 'color': '#13c2c2', 'icon': 'transaction', 'description': '比特币、以太坊等', 'sort_order': 1},
            {'name': 'NFT', 'color': '#36cfc9', 'icon': 'picture', 'description': '数字艺术品、数字收藏品', 'sort_order': 2},
            {'name': '游戏资产', 'color': '#5cdbd3', 'icon': 'trophy', 'description': '游戏装备、游戏币等', 'sort_order': 3},
        ]
    },
    {
        'name': '其他资产',
        'color': '#8c8c8c',
        'icon': 'appstore',
        'description': '其他类型的资产',
        'sort_order': 8,
        'children': [
            {'name': '会员权益', 'color': '#8c8c8c', 'icon': 'star', 'description': '各类会员卡、积分等', 'sort_order': 1},
            {'name': '预付款', 'color': '#a6a6a6', 'icon': 'credit-card', 'description': '预付卡、储值卡等', 'sort_order': 2},
            {'name': '其他', 'color': '#bfbfbf', 'icon': 'folder', 'description': '其他未分类资产', 'sort_order': 3},
        ]
    },
]
