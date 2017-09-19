.. _ysc_note:


云审查前端开发
################


.. contents:: 目录

--------------------

本篇文章，尝试对云审查项目前端开发中涉及到的知识及相关功能实现，
做个总结，供参考。


页面动态数据获取
=================

云审查项目设计过程中，首先是由郑老师设计出静态页面，然后通过Python Dango框架，
按照MTV模式，在页面中获取真实数据，并进行展现。

两种获取数据方式
+++++++++++++++++

在页面展示真实数据时，包括两部分：HTML和js。下面以下图为例，进行说明：

.. figure:: /_static/images/html_js_data.png
    :scale: 100
    :align: center

在上述页面中，标记为圆圈的部分为echart图表，图表数据在js代码中进行定义。
而标记为方形的，数据由页面HTML部分进行控制。这两种动态数据获取方式，截然不同。这一点十分重要：

- 对标记为方形的部分，我们只需要对页面模板相关地方进行标记，然后在view层返回字典对象对模板进行渲染，
  然后动态数据在渲染后的页面中就可以显示出来。了解Django框架的，应该都熟悉这一点。
    
  .. figure:: /_static/images/template_html.png
     :scale: 100
     :align: center

  .. figure:: /_static/images/context_views.png
     :scale: 100
     :align: center

     模板动态数据标记与渲染
  
- 对于echarts图表，我们要在该图表对应的js函数中，发起ajax请求获取动态数据，然后将返回的数据，
  转换成相应的格式。如下图所示：  

  .. figure:: /_static/images/ajax_get_data.png
     :scale: 100
     :align: center

     echarts图表，发起ajax请求，动态获取数据!

  针对js图表发起的ajax请求，在后端view层中，编写URL请求对应的处理函数，然后返回json格式化数据。
  
  .. figure:: /_static/images/ajax_url.png
     :scale: 100
     :align: center

  .. figure:: /_static/images/ajax_views.png
     :scale: 100
     :align: center
 
     ajax请求对应的views处理！

ajax请求处理
++++++++++++++

对于页面ajax请求的处理实现上，我们使用了一些技巧，我们结合下面的页面，简要说明。

.. figure:: /_static/images/trendanalysis.png
    :scale: 100
    :align: center

如上图所示页面中，有十多个echarts图表，如果每个图表获取动态数据的ajax请求都单独定义一个url的话，
那么urls.py需要定义十多项，会显得很庞杂。

我们的处理方式是，对每个页面的所有ajax请求，只定义一个url。那么后端又怎么区分，
是哪个图表发起的ajax请求呢？为此，我们会在每个请求的URL上，拼上查询字符串charts，
代表发起ajax请求的具体图表。最终页面的某个图表，发起的ajax请求URL地址会形如：
http://192.168.60.213:9999/cscloudwatch/cssec/webids/trendanalysis/attacktrend/get_charts_data?timerange=1&charts=sec_ids_trend_attack_contr_type&_=1505107971591

.. figure:: /_static/images/ajax_params.png
    :scale: 100
    :align: center

至于timerange参数，某些echarts图表，可以通过下拉列表，查看当天、7天、15天等时间范围的数据，
通过timerange参数，表示图表想展示的数据的时间范围，然后views层根据charts和timerange参数，
获取对应的数据并返回。

.. figure:: /_static/images/charts_data_views.png
    :scale: 100
    :align: center


select点击事件
===============

如上图所示，一个页面有很多下拉列表，需要根据点击的下拉列表，获取选择的时间范围和对应的echarts图表，
可以这样实现：

::

    $("select").change(function(){
        // 获取选择的时间范围
        var timerange=$(this).val();
        //获取点击的是哪个下拉列表
        var charts = $(this).attr('name');

        // 获取select所选择的文本值
        var business_name = $(this).find('option:selected').text();
        // 获取id为select_yewu的select的选择文本值
        var business_name = $('#select_yewu').find('option:selected').text();

        var params = {"url":url,"timerange":timerange,"charts":charts};
        console.info(params)
        if(charts == "attect_event_undercontrol"){
          show_attect_event_undercontrol(params)
        }
        else if(charts == "sec_ids_trend_attack_type_top"){
          show_attack_type_top10(params)
        }
    })

::

    <select name="attect_event_undercontrol" class="select">
        <option value="1">今日</option>
        <option value="7">7天</option>
        <option value="15">15天</option>
        <option value="30">月统计</option>
        <option value="365">年统计</option>
    </select>

另外注意：$("select").change()表示具有class="select"属性的<select>标签的点击事件。
$("#select").change()表示id="select"的标签的点击事件。

.. note::

    注意，在编辑HTML时，注意避免标签的id一样，虽然即使一样也不会报错，
    但是有时会出现难以理解、难以调试的问题。

设置html值
===========

有时，需要动态修改页面某些部分的显示文本。如下图：

.. figure:: /_static/images/modify_html.png
    :scale: 100
    :align: center

::

    <td width="200" id="select_yewu_td" align="center" valign="middle"> 当前业务系统：{{show_select_yewu}}</td>

::

    var business_name = $('#select_yewu').find('option:selected').text();
    $('#select_yewu_td').html("当前业务系统：" + business_name);

数据分页
=========

在页面进行日志等信息展示时，有时需要展示的记录很多，这时我们就需要考虑进行数据分页。

数据分页包括两种：

- 数据真分页，即每次只返回固定条数的记录。然后点击页面上下一页时，再返回另外固定数量的记录。
- 数据假分页，即一次返回所有的记录，然后在前端，通过js技巧进行控制，达到类似于分页的效果。

这里，我们使用的数据真分页。这个问题比我想象的复杂，主要是在于点击分页的脚注(动态生成)这一块，
边界条件很多。如下面所示几个截图：

.. figure:: /_static/images/cut_page_1.png
    :scale: 100
    :align: center

.. figure:: /_static/images/cut_page_2.png
    :scale: 100
    :align: center

    分页脚注边界

下面来看分页的实现代码：

.. figure:: /_static/images/cut_page_3.png
    :scale: 100
    :align: center

    分页模板层

.. figure:: /_static/images/cut_page_4.png
    :scale: 100
    :align: center

    分页views层

因为Django模板语言的编程能力很弱，因此，尽量在views层计算好相关信息(如上一页，下一页，分页数字列表等)，
然后在模板层进行渲染。

**虽然在分页控制上，我试图尽量考虑全边界条件，但还是遇到一些难以处理或者处理起来很是复杂的问题，比如"末页"、
数据量少等。这些边界问题，待以后进一步完善。**

文件下载
=========

为了配合后期云上贵州流量镜像数据包监控，加上了一个如下页面：

.. figure:: /_static/images/filecheck.png
    :scale: 100
    :align: center

这个页面，需求是想把保存在服务器某个目录下的流量镜像数据包显示出来，并提供下载功能。

这里对于单文件下载，我们只需要在文件链接里，加上download属性，然后点击链接，
会自动弹出对话框，提示进行保存。

.. figure:: /_static/images/download_link.png
    :scale: 100
    :align: center

    <a>标签加上download属性，点击链接自动弹出对话框

对于多文件下载，在网络上搜索了相关解决方案，都不太可行(基本都是基于js多文件下载)。
后来，我尝试遍历table并依次下载每一个要下载的文件，这种方式，但是会弹出很多个对话框提示保存文件，
十分烦人。

不得已，我构思了一个新方法，基本思路是：点击下载按钮时，将要下载的文件名称保存下来，
并发起ajax请求。在服务端：接收请求并从请求信息中提取出要下载的文件名称，
然后把要下载的文件进行打包归档，并给客户端返回打包后文件名称。
最后客户端下载该打包文件！

来看具体代码：

::

  $('#download').click(function(){
      var download_url = [];
      //遍历table的tbody部分每一行
      $("#file_list").find("tr").each(function(){
          var tdArr = $(this).children();
          // 获取复选框选中状态
          var checked = tdArr.eq(1).find('input').is(':checked');
          // 获取文件链接，(后端根据文件链接获取文件名称然后生成压缩文件)
          var href = tdArr.eq(6).find('a').attr('href');
          if(checked)
              //window.open(href)
              download_url.push(href);
      });
      
      console.info(download_url);
      var url = window.location.href;
      console.info(url);

      var jsondata;

      $.ajax({
        url: url + 'multidownload',
        data: {urls:JSON.stringify(download_url)},
        cache: false,
        async : false,
        dataType: "json",
        success: function (data ,textStatus, jqXHR)
        {     
        //console.log("Get Data From Server!!");
        jsondata = data; 
        },
        error:function (XMLHttpRequest, textStatus, errorThrown)
        {
        console.log("Request Error！！");
        }
      });
     
      // 下载压缩文件
      window.open('/static/cloudwatch/filecheck/' + jsondata)

  });
 
下面渲染后的页面数据表格！

::

    <table width="100%" border="0" cellspacing="0" cellpadding="0" id="senfe2">
      <tr>
        <td width="30" class="bg_td_t2">&nbsp;</td>
        <td width="30"><input id="check_all" type="checkbox" class="checkbox">全选</td>
        <td width="46" class="bg_td_t2">文件名称</td>
        <td width="140" class="bg_td_t2">文件大小</td>
        <td width="140" class="bg_td_t2">文件所有者</td>
        <td width="140" class="bg_td_t2">最后修改时间</td>
        <td width="40" align="center" class="bg_td_t2">下载</td>
      </tr>
      <tbody id="file_list">
      
      <tr > 
        <td width="26"><img src="/static/cloudwatch/images/ico1604.png"/></td>
        <td><input type="checkbox" class="checkbox" name='check_td'></td>
        <td>call_stack.log</td>
        <td width="140">1.38 KB</td>
        <td width="140">root</td>
        <td width="140">2017-09-06 15:44:53</td>
        <td  width="40" align="center" class='row_click'>
            <a download href="/static/cloudwatch/filecheck/call_stack.log"><img src="/static/cloudwatch/images/ico1601.png" border="0"/></a></td>
      </tr>
      
      <tr > 
        <td width="26"><img src="/static/cloudwatch/images/ico1604.png"/></td>
        <td><input type="checkbox" class="checkbox" name='check_td'></td>
        <td>test.py</td>
        <td width="140">548 B</td>
        <td width="140">root</td>
        <td width="140">2017-09-06 15:44:53</td>
        <td  width="40" align="center" class='row_click'>
            <a download href="/static/cloudwatch/filecheck/test.py"><img src="/static/cloudwatch/images/ico1601.png" border="0"/></a></td>
      </tr>
      </tbody>
    </table>


.. figure:: /_static/images/multidownload_url.png
    :scale: 100
    :align: center

.. figure:: /_static/images/multidownload_views.png
    :scale: 100
    :align: center

.. figure:: /_static/images/make_tar_file.png
    :scale: 100
    :align: center

    多文件下载后端实现部分

.. figure:: /_static/images/multidownload_file.png
    :scale: 100
    :align: center

    多文件下载

.. figure:: /_static/images/make_tar_file_2.png
    :scale: 100
    :align: center

    后端会生成压缩文件


复选框
=======

参考上面的文件下载，有时我们需要在页面中，根据总控制复选框的"全选"和"取消全选"设置其他复选框的选中状态，
可以这样实现：

::

	<table>
	<tr>
		<td width="30"><input id="check_all" type="checkbox" class="checkbox">全选</td>
		<td><input type="checkbox" class="checkbox" name='check_td'></td>
		<td><input type="checkbox" class="checkbox" name='check_td'></td>
		<td><input type="checkbox" class="checkbox" name='check_td'></td>
	</tr>
	</table>

::

  $('#check_all').click(function(){
        var value = $('#check_all').is(':checked');
        console.info(value);
        //$("checkbox").attr("checked",value); 
        $("input[type='checkbox'][name='check_td']").prop("checked",value);
  });


button标签与表单
=================

<button>标签定义一个按钮。

<button>控件与<input type="button">相比，提供了更为强大的功能和更丰富的内容。
<button>与</button>标签之间的所有内容都是按钮的内容，
其中包括任何可接受的正文内容，比如文本或多媒体内容。例如，
我们可以在按钮中包括一个图像和相关的文本，用它们在按钮中创建一个吸引人的标记图像。

.. note::

    请始终为按钮规定 type 属性。Internet Explorer 的默认类型
    是 "button"，而其他浏览器中（包括 W3C 规范）的默认值是 "submit"。

    .. figure:: /_static/images/button_type.png
       :scale: 100
       :align: center

       button type 属性取值

.. important::

    关于button，自己在阅读openstack代码时一直有一点困惑的地方，就是在点击
    按钮时，对应的处理程序在哪里。现在把这个问题记录下来，以作总结。


- button点击按钮后，假如在页面js中有相关的处理，则会调用相应的事件处理程序.(在前端执行，与服务端无关)

  .. literalinclude:: /_static/src/button_test.html
     :language: html
     :linenos:


  如上代码，点击按钮后，都会在调用客户端的click事件处理程序。

- 假如button包含在form中，那么点击表单，则会向服务端提交表单。然后服务端会调用相应的表单处理程序。

  对于django框架来说，通过from提交时 的action，依据URL匹配来决定调用的view(表单处理程序)。

  比如在《django book 2.0》给出的示例中，表单的action="/search/"，因此点击按钮，会根据url.py，决定调用
  view.py的search函数。

  .. figure:: /_static/images/form_temp.png
     :scale: 100
     :align: center

     表单的action属性

  .. figure:: /_static/images/button_action.png
     :scale: 100
     :align: center

     提交表单时服务端会调用view.search 处理程序。

  至于表单提交的GET和POST方法，会在另外一篇文章专门分析。


input type="submit" 和"button"区别分析
=======================================

在一个页面上画一个按钮，有四种办法：

- <input type="button" /> 这就是一个按钮。如果你不写javascript 的话，按下去什么也不会发生。
- <input type="submit" /> 这样的按钮用户点击之后会自动提交 form，除非你写了javascript 阻止它。
- <button> 这个按钮放在 form 中也会点击自动提交，比前两个的优点是按钮
  的内容不光可以有文字，还可以有图片等多媒体内容。（当然，前两个用图片背
  景也可以做到）。它的缺点是不同的浏览器得到的 value 值不同；可能还有其他的浏览器兼容问题
- 其他标签，例如 a, img, span, div，然后用图片把它伪装成一个按钮。

可以参考\ `[原]<button>和<input type="button"> 的区别 <http://www.cnblogs.com/purediy/archive/2012/06/10/2544184.html>`__\


---------------------

参考
=====

.. [#] http://www.w3school.com.cn/tags/att_button_type.asp
.. [#] https://www.zhihu.com/question/20839977
.. [#] http://djangobook.py3k.cn/2.0/chapter07/

