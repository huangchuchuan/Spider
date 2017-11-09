# 京东商品评论爬虫

## 工作原理
爬虫根据关键字，在京东搜索页面上搜索出相关商品，从而得到对应的商品id.
然后通过商品id来对相应的评论页进行爬取

## 使用方法
在`jdcomment.py`里面更改`KEYWORD`的值来对不同商品的评论进行爬取

## 京东api说明
### 商品搜索api
1. `SEARCH_URL`接口会校验请求头中的`Host`, `X-Requested-With`和`Referer`部分，所以相关参数要严格设置
2. 京东商品加载方式是典型的二段式，通过检查元素发现，渲染出来的html代码页数是奇数的等差数列`1,3,5,7...`
在接口中需要进行两次请求才能把所有商品信息获取到
3. 京东请求奇数页返回30个结果，请求偶数页需要把前30个结果的商品id组成逗号分隔的字符串传回来获取剩余的30个商品

#### url
```python
# 搜索页
SEARCH_REFERER = 'https://search.jd.com/Search?keyword={keyword}&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq={keyword}&page={page_keyword}&s={start_item}&click=0'
# 搜索结果接口
SEARCH_URL = 'https://search.jd.com/s_new.php'
```
#### headers
```python
DEFAULT_REQUEST_HEADERS = {
    'Host': 'search.jd.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': SEARCH_REFERER,
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
}
```
#### params
```python
DATA = {
    'keyword': KEYWORD,
    'enc': 'utf-8',
    'qrst': '1',
    'rt': '1',
    'stop': '1',
    'vt': '2',
    'wq': KEYWORD,
    'page': PAGE,
    's': START_ITEM,
    'psort': '4',  # 按照评论数排序
    'scrolling': 'y',
    'tpl': '1_M',
    'log_id': '1510033965.96458',
    'show_items': '',  # 偶数页需要把奇数页获取的商品id作为参数传回
}
```
#### response
响应是html代码
```html
<li data-sku="1528270" class="gl-item">
	<div class="gl-i-wrap">
	    <div class="p-img">
		    <a target="_blank" title="【258元，前600名领券再半价！11日0点开抢，敬请期待！更多1元5折产品攻略，点此直达！】" href="//item.jd.com/1528270.html" onclick="searchlog(1,1528270,30,2,'','flagsClk=1614811784')">
			    <img width="220" height="220" class="err-product" data-img="1" src="//img10.360buyimg.com/n7/jfs/t11632/232/1337422464/351394/2f2e6b8b/5a003401N58324b9b.jpg" />
            </a>
        <div data-catid="14204" data-venid="1000006842" data-presale="0" class="picon" style="background:url(//img30.360buyimg.com/jgsq-productsoa/jfs/t10744/359/434392933/1550/64b961e/59cf1f1cN6dabcc8b.png) no-repeat 0 0;_background-image:none;_filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(src='//img30.360buyimg.com/jgsq-productsoa/jfs/t10744/359/434392933/1550/64b961e/59cf1f1cN6dabcc8b.png',sizingMethod='noscale');"></div>
		</div>
		<div class="p-price">
            <strong class="J_1528270" data-done="1"><em>￥</em><i>291.00</i></strong>
        </div>
		<div class="p-name p-name-type-2">
			<a target="_blank" title="【258元，前600名领券再半价！11日0点开抢，敬请期待！更多1元5折产品攻略，点此直达！】" href="//item.jd.com/1528270.html" onclick="searchlog(1,1528270,30,1,'','flagsClk=1614811784')">
				<em><img class="p-tag3" src="//img14.360buyimg.com/uba/jfs/t6919/268/501386350/1257/92e5fb39/5976fcf9Nd915775f.png" />爱康国宾（ikang）<font class="skcolor_ljg">体检</font>卡 常规基础<font class="skcolor_ljg">套餐</font> 全国门店通用</em>
				<i class="promo-words" id="J_AD_1528270">【258元，前600名领券再半价！11日0点开抢，敬请期待！更多1元5折产品攻略，点此直达！】</i>
			</a>
		</div>
		<div class="p-commit">
			<strong><a id="J_comment_1528270" target="_blank" href="//item.jd.com/1528270.html#comment" onclick="searchlog(1,1528270,30,3,'','flagsClk=1614811784')">1000+</a>条评价</strong>
		</div>
		<div class="p-shop" data-selfware="1" data-score="5" data-reputation="97">
            <span class="J_im_icon"><a target="_blank" class="curr-shop" onclick="searchlog(1,1000006842,0,58)" href="//mall.jd.com/index-1000006842.html" title="爱康国宾自营旗舰店">爱康国宾自营旗舰店</a></span>					</div>
			<div class="p-icons" id="J_pro_1528270" data-done="1">
				<i class="goods-icons J-picon-tips J-picon-fix" data-idx="1" data-tips="京东自营，品质保障">自营</i>
			</div>
		<div class="p-operate">
			<a class="p-o-btn contrast J_contrast" data-sku="1528270" href="javascript:;" onclick="searchlog(1,1528270,30,6,'','flagsClk=1614811784')"><i></i>对比</a>
			<a class="p-o-btn focus J_focus" data-sku="1528270" href="javascript:;" onclick="searchlog(1,1528270,30,5,'','flagsClk=1614811784')"><i></i>关注</a>
			<a class="p-o-btn addcart" href="//cart.jd.com/gate.action?pid=1528270&pcount=1&ptype=1" target="_blank" onclick="searchlog(1,1528270,30,4,'','flagsClk=1614811784')" data-limit="0"><i></i>加入购物车</a>
		</div>
	</div>
</li>
```

### 评论搜索api
1. `COMMENT_URL`接口会校验请求头中的`Host`和`Referer`部分，所以相关参数要严格设置
2. `page`从0开始，不分奇偶页

#### url
```python
# 评论页
COMMENT_REFERER = 'https://item.jd.com/ID.html'
# 评论结果接口
COMMENT_URL = 'https://sclub.jd.com/comment/productPageComments.action'
```
#### headers
```python
COMMENT_REQUEST_HEADERS = {
    'Host': 'sclub.jd.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://item.jd.com/12571462129.html',  # 对应商品的页面
    'Connection': 'keep-alive',
}
```
#### params
```python
COMMENT_DATA = {
    'callback': 'fetchJSON_comment98vv152',  # 后面三个数字随机
    'productId': '12571462129',  # 商品id
    'score': '0',
    'sortType': '5',
    'page': '0',  # 评论第x页
    'pageSize': '10',
    'isShadowSku': '0',
    'fold': '1',
}
```
#### response
```javascript
fetchJSON_comment98vv122({
	"productAttr": null,
	"productCommentSummary": {
		"goodRateShow": 97,
		"poorRateShow": 1,
		"poorCountStr": "10+",
		"averageScore": 5,
		"generalCountStr": "20+",
		"oneYear": 0,
		"showCount": 80,
		"showCountStr": "80+",
		"goodCount": 1000,
		"generalRate": 0.021,
		"generalCount": 20,
		"skuId": 2667959,
		"goodCountStr": "1000+",
		"poorRate": 0.011,
		"afterCount": 3,
		"goodRateStyle": 145,
		"poorCount": 10,
		"skuIds": null,
		"poorRateStyle": 2,
		"generalRateStyle": 3,
		"commentCountStr": "1000+",
		"commentCount": 1000,
		"productId": 2667959,
		"afterCountStr": "3",
		"defaultGoodCount": 300,
		"goodRate": 0.968,
		"generalRateShow": 2,
		"defaultGoodCountStr": "300+"
	},
	"hotCommentTagStatistics": [{
		"id": "1467260",
		"name": "送货快",
		"status": 0,
		"rid": "16727",
		"productId": 2667959,
		"count": 1,
		"modified": "2017-01-09 11:44:35",
		"type": 0,
		"canBeFiltered": false
	}],
	"jwotestProduct": "99",
	"maxPage": 66,
	"score": 0,
	"soType": 5,
	"imageListCount": 116,
	"vTagStatistics": null,
	"comments": [{
		"id": 10827600829,
		"guid": "095f5c63-6c5d-4e7b-af58-5fe05c2003c7",
		"content": "检查完了，本人是在广州使用，服务态度没得说，非常好，每个科室医生检查详细，还有送早餐，以后每年检查都会去爱康国宾。",
		"creationTime": "2017-10-01 17:54:31",
		"isTop": false,
		"referenceId": "2667959",
		"referenceImage": "jfs/t7381/348/4133538107/380092/22e1dcab/59ffb879N4d2e5230.jpg",
		"referenceName": "爱康国宾（ikang）体检卡 深爱老公老婆体检套餐 全国门店通用",
		"referenceTime": "2017-09-07 18:29:05",
		"referenceType": "Product",
		"referenceTypeId": 0,
		"firstCategory": 9192,
		"secondCategory": 14203,
		"thirdCategory": 14204,
		"replyCount": 0,
		"score": 5,
		"status": 1,
		"title": "",
		"usefulVoteCount": 1,
		"uselessVoteCount": 0,
		"userImage": "misc.360buyimg.com/user/myjd-2015/css/i/peisong.jpg",
		"userImageUrl": "misc.360buyimg.com/user/myjd-2015/css/i/peisong.jpg",
		"userLevelId": "105",
		"userProvince": "",
		"viewCount": 0,
		"orderId": 0,
		"isReplyGrade": false,
		"nickname": "帅***飞",
		"userClient": 2,
		"images": [{
			"id": 415870745,
			"associateId": 263301426,
			"productId": 0,
			"imgUrl": "//img30.360buyimg.com/n0/s128x96_jfs/t10873/14/490911554/1437197/5ba03569/59d11223Na36b22bd.jpg",
			"available": 1,
			"pin": "",
			"dealt": 0,
			"imgTitle": "",
			"isMain": 0,
			"jShow": 0
		}],
		"showOrderComment": {
			"id": 263301426,
			"guid": "9a24cb67-b7e0-40a6-ac1c-9960ff5d2707",
			"content": "检查完了，本人是在广州使用，服务态度没得说，非常好，每个科室医生检查详细，还有送早餐，以后每年检查都会去爱康国宾。",
			"creationTime": "2017-10-02 00:04:51",
			"isTop": false,
			"referenceId": "2667959",
			"referenceType": "Order",
			"referenceTypeId": 0,
			"firstCategory": 0,
			"secondCategory": 0,
			"thirdCategory": 0,
			"replyCount": 0,
			"score": 0,
			"status": 1,
			"usefulVoteCount": 0,
			"uselessVoteCount": 0,
			"userProvince": "",
			"viewCount": 0,
			"orderId": 0,
			"isReplyGrade": false,
			"userClient": 2,
			"isDeal": 1,
			"integral": -20,
			"userImgFlag": 0,
			"anonymousFlag": 1,
			"recommend": false,
			"userLevelColor": "#666666",
			"userClientShow": "来自京东iPhone客户端",
			"isMobile": true
		},
		"mergeOrderStatus": 2,
		"discussionId": 263301426,
		"productColor": "深爱老公老婆",
		"productSize": "",
		"imageCount": 3,
		"integral": -20,
		"userImgFlag": 0,
		"anonymousFlag": 1,
		"userLevelName": "PLUS会员",
		"plusAvailable": 201,
		"userExpValue": 31721,
		"productSales": [],
		"recommend": true,
		"userLevelColor": "#e1a10a",
		"userClientShow": "来自京东iPhone客户端",
		"isMobile": true,
		"days": 24,
		"afterDays": 0
	},
	]
});
```