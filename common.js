var filterData = {};
var dataset = [];
var provinceData = [];
var operatorData = [];
var chipsetData = [];
var total = 0;
var rows = 10;
var timer = null;
var middlewaretime = '';
var searchData = {
  "productClass": "ALL",
  "province": "ALL",
  "offset": 0,
  "midware": "ALL",
  "chipset": "ALL",
  "rows": 100,
  "operator": "ALL",
  "orderBy":"firmwareDate"
}

$(function () {
  loginCheck();
  $.ajax({
    type: "POST",
    url: "updateCfg.do",
    async: false
  });

  $.ajax({
    type: "POST",
    url: "js/stbrelease.cfg.json",
    async: false,
    success: function (data) {
      filterData = data;
      provinceData = data.Province;
      operatorData = data.Operator;
      chipsetData = data.chipset;
      initData(data);
    }
  });

  //
  $.ajax({
    type: 'POST',
    url: "querySomeNotes.do",
    data: searchData,
    async: false,
    success: function (data) {
      dataset = creatTableData(data.notes);
      total = data.Total;
      rows = data.rows;
      $('#table1_info').text("共 " + data.Total + " 条数据，每页显示 " + data.rows + " 条，共 " + Math.ceil(data.Total / rows) + " 页");
    }
  });
  drawTable(dataset);
  pageModel(total, rows);
});

function loginCheck() {
  $.ajax({
    type: "POST",
    url: "getLoginStatus.do",
    async: false,
    success: function (data) {
      if (data.username != "") {
        $("#loginName").text("欢迎：" + data.username);
        $("#signOutButton").show();
        $('#loginButton').hide();
        $("#AddBtn").show();
      } else {
        $("#loginName").text("");
        $("#signOutButton").hide();
        $('#loginButton').show();
        $("#AddBtn").hide();
      }
    }
  });
}

//下拉选择数据处理模块
function initData(data) {
  var product = document.getElementById("product");
  var province = document.getElementById("province");
  var operator = document.getElementById("operator");
  var chip = document.getElementById("chip");
  var middleware = document.getElementById("middleware");

  var add_product = document.getElementById("add_product");
  var add_province = document.getElementById("add_province");
  var add_operator = document.getElementById("add_operator");
  var add_chip = document.getElementById("add_chip");
  var add_wifi = document.getElementById("add_wifi");
  var add_middleware = document.getElementById("add_middleware");

  var update_middleware = document.getElementById("update_middleware");

  var ordertype = document.getElementById("ordertype");
  ordertype.options.add(new Option("按日期查看", "firmwareDate"));
  ordertype.options.add(new Option("按版本号查看", "swVersion"));

  data.productClass.map(function (k) {
    product.options.add(new Option(k, k));
    if (k == "ALL") {
      add_product.options.add(new Option("", ""));
    } else {
      add_product.options.add(new Option(k, k));
    }

  });

  data.Province.map(function (k) {
    province.options.add(new Option(k.name, k.Shorthand));
    if (k.name == "ALL") {
      add_province.options.add(new Option("", ""));
    } else {
      add_province.options.add(new Option(k.name, k.Shorthand));
    }
  });

  data.Operator.map(function (k) {
    operator.options.add(new Option(k.name, k.Shorthand));
    if (k.name == "ALL") {
      add_operator.options.add(new Option("", ""));
    } else {
      add_operator.options.add(new Option(k.name, k.Shorthand));
    }
  });

  data.chipset.map(function (k) {
    chip.options.add(new Option(k, k));
    if (k == "ALL") {
      add_chip.options.add(new Option("", ""));
    } else {
      add_chip.options.add(new Option(k, k));
    }
  });

  data.middleware.map(function (k) {
    middleware.options.add(new Option(k, k));
    if (k == "ALL") {
      add_middleware.options.add(new Option("", ""));
    } else {
      add_middleware.options.add(new Option(k, k));
      update_middleware.options.add(new Option(k, k));
    }
  });

  add_wifi.options.add(new Option("", ""));
  data.wifiType.map(function (k) {
    add_wifi.options.add(new Option(k, k));
  });
}

/*画表格模块*/
//表格数据处理
function creatTableData(data) {
  let arr2 = [];
  for (let i = 0; i < data.length; i++) {
    (function (i) {
      let arr = [];
      arr[0] = data[i].productClass;
      //k.name, k.Shorthand 
      let province_operator = '';
      let findprov = false;
      let findoper = false;
      provinceData.map(function (k) {
        if (data[i].province.toLowerCase() == k.Shorthand) {
          province_operator = k.name;
          findprov = true;
        }
      });
      if (!findprov) {
        province_operator = data[i].province;
      }

      operatorData.map(function (k) {
        if (data[i].operator == k.Shorthand) {
          province_operator = province_operator + k.name;
          findoper = true;
        }
        if (data[i].operator == k.name) {
          province_operator = province_operator + k.name;
          findoper = true;
        }
      });
      if (!findoper) {
        province_operator = province_operator + data[i].operator;
      }
      if (province_operator == '工厂工厂') {
        province_operator = '工厂';
      }
      arr[1] = province_operator;
      arr[2] = data[i].chipset + ((data[i].chipsetDate != '') ? '_' + data[i].chipsetDate : '');
      arr[3] = data[i].midware + ((data[i].midwareDate != '') ? '_' + data[i].midwareDate : '');
      arr[4] = data[i].swVersion;
      arr[5] = data[i].author;
      arr[6] = data[i].firmwareDate;
      arr[7] = '<a href="' + data[i].noteAddr + '" target="_blank">下载</a>';
      arr[8] = '<a href="' + data[i].firmwareAddr + '" target="_blank">下载</a>';
      var isBaseVersion = data[i].isBaseVersion;// isBaseVersion
      var olddate = 20180208;
      var datedata = parseInt( data[i].firmwareDate);
      if(olddate<=datedata){
    	  if (isBaseVersion == "1"){
    		  arr[9] = '<button class="table-normal-btn compare-btn">初版</button>';
    	  }else if(data[i].swVersion == "S-010W-AV2A_SW_G_ZY_CTJC_R1.00.11"){
          arr[9] = '<button class="table-normal-btn compare-btn disabled-btn" disabled>比较</button>';
        }else{
    		  arr[9] = '<button class="table-normal-btn compare-btn">比较</button>';
        }
      }else{
        arr[9] = '<button class="table-normal-btn compare-btn disabled-btn" disabled>比较</button>';
      }
      arr[10] = '<button class="table-normal-btn update-btn">编辑</button>';
      arr2.push(arr);
    })(i);
  }
  return arr2;
}
//画表
function drawTable(dataset) {
  clearTable('#table1');
  var columns = null;
  if ($("#loginName").text() == "") {
    columns = [{
        "title": "产品"
      },
      {
        "title": "省份运营商"
      },
      {
        "title": "芯片"
      },
      {
        "title": "中间件"
      },
      {
        "title": "版本号"
      },
      {
        "title": "作者"
      },
      {
        "title": "日期"
      },
      {
        "title": "ReleaseNote"
      },
      {
        "title": "固件地址"
      },
      {
        "title": "版本差异"
      }
    ];
  } else {
    columns = [{
        "title": "产品"
      },
      {
        "title": "省份运营商"
      },
      {
        "title": "芯片"
      },
      {
        "title": "中间件"
      },
      {
        "title": "版本号"
      },
      {
        "title": "作者"
      },
      {
        "title": "日期"
      },
      {
        "title": "ReleaseNote"
      },
      {
        "title": "固件地址"
      },
      {
        "title": "版本差异"
      },
      {
        "title": "编辑"
      }
    ]
  }

  $('#table1').DataTable({
    searching: false,
    paging: false,
    ordering: false,
    bScrollCollapse: true,
    bInfo: false,
    // aLengthMenu : [100, 200, 500,1000], //更改显示记录数选项  
    iDisplayLength: 100, //默认显示的记录数 
    data: dataset,
    columns: columns,
    sPaginationType: "full_numbers",
    oLanguage: {
      sLengthMenu: "每页显示 _MENU_ 条记录",
      sZeroRecords: "抱歉， 没有找到",
      sInfo: "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
      sInfoEmpty: "没有数据",
      sInfoFiltered: "(从 _MAX_ 条数据中检索)",
      sZeroRecords: "没有检索到数据",
      sSearch: "名称:",
      oPaginate: {
        sFirst: "首页",
        sPrevious: "上一页",
        sNext: "下一页",
        sLast: "尾页"
      }
    }
  });
  /*差异模块*/
  $("#table1 tbody").on('click', 'td button.compare-btn', function () {
    var tr = $(this).closest('tr');
    var swVersion = tr.find("td").eq(4).text();
    var chipset = tr.find("td").eq(2).text();
    var chip = '';
    for (let i = 0; i < chipsetData.length; i++) {
      if (chipset.indexOf(chipsetData[i]) == 0) {
        chip = chipsetData[i];
        break;
      }

    }

    $.ajax({
      type: "POST",
      url: "getDiffFile.do",
      data: {
        "swVersion": swVersion,
        "chipset": chip
      },
      async: false,
      success: function (data) {
        if (data && data.result == "OK") {
          var alldata;
          for (let i = 0;i < data.filename.length; i++){
              $.ajax({
                type: "post",
                url: "data/" + data.filename[i],
                async: false,
                success: function (data) {
                  alldata=alldata+data
                }
              });
		  }
        $("#difference_text").html('<pre>' + alldata + '</pre>');
        } else {
          if (data && data.reason) {
            $("#difference_text").html('<pre>' + data.reason + '</pre>');
          } else {
            $("#difference_text").html('<pre>脚本异常，无法显示</pre>');
          }
        }

      }
    });
    $("#difference_modal").show();
  });

  /*修改模块*/
  $("#table1 tbody").on('click', 'td button.update-btn', function () {
    var tr = $(this).closest('tr');
    //版本号
    var swVersion = tr.find("td").eq(4).text();  
    $("#update_swVersion").html(swVersion);
    //中间件 中间件输入时间
    let middletime = tr.find("td").eq(3).text();   
    let update_middleware = "";
    let update_middleware_time = "";
    if(middletime.indexOf("_") != -1){
      middletime = middletime.split("_");
      update_middleware = middletime[0];
      update_middleware_time = middletime[1];
    }else if(middletime != ""){
      update_middleware = middletime;
    }
    $("#update_middleware").val(update_middleware);
    if(update_middleware == "noMidware"){
      $("#update_middleware_time").val("");
      $("#update_middleware_time").prop("disabled",true);
    }else{
      $("#update_middleware_time").val(update_middleware_time);
      middlewaretime = update_middleware_time;
      $("#update_middleware_time").prop("disabled",false);
    }
    //芯片输入时间
    let rktime = tr.find("td").eq(2).text();   
    let update_rk_time = "";
    if(rktime.indexOf("_") != -1){
      rktime = rktime.split("_");
      update_rk_time = rktime[1];
    }else if(rktime != ""){
      update_rk_time = "";
    }
    $("#update_rk_time").val(update_rk_time);
    //固件生成时间
    let update_build_time = tr.find("td").eq(6).text();   
    $("#update_build_time").val(update_build_time);
    //作者
    let update_author = tr.find("td").eq(5).text();   
    $("#update_author").val(update_author);
    //ReleaseNote地址
    var update_ReleaseNotes_download = tr.find("td").eq(7).html();  
    update_ReleaseNotes_download = update_ReleaseNotes_download.split('"');
    $("#update_ReleaseNotes_download").val(update_ReleaseNotes_download[1]);
    //固件地址
    var update_build_download = tr.find("td").eq(8).html();   
    update_build_download = update_build_download.split('"');
    var update_build_download2 = update_build_download[1].replace("http://172.24.170.213/E%3A/stb/IP_STB%E7%8E%B0%E5%9C%BA%E7%89%88%E6%9C%AC/","").replace("http://172.24.170.213/E%3A/stb/IP_STB现场版本/","");
    $("#update_build_download").val(update_build_download2);

    $("#err_upadte_msg").html("");
    $("#update_modal").show();

  });

}
/*差异模块*/
$("#diffCloseBtn").on('click', function () {
  $("#difference_modal").hide();
});
/*修改模块*/

$("#update_middleware").on("change",function(){
  
  if($("#update_middleware").val() == "noMidware"){
    $("#update_middleware_time").prop("disabled",true);
    $("#update_middleware_time").val("");
  }else{
    $("#update_middleware_time").prop("disabled",false);
    $("#update_middleware_time").val(middlewaretime);
  }
});

$("#update_apply").unbind('click').on('click', function () {
  let err_msg = '';
  if($("#update_middleware").val() != "noMidware" && $("#update_middleware").val() != ""){
    err_msg = checkInputStr($("#update_middleware_time").val(), "中间件输入时间", "time");
    if (err_msg != "") {
      $("#err_upadte_msg").html(err_msg);
      return false;
    }
  }
  err_msg = checkInputStr($("#update_rk_time").val(), "芯片输入时间", "time");
  if (err_msg != "") {
  $("#err_upadte_msg").html(err_msg);
  return false;
  }
  
  err_msg = checkInputStr($("#update_build_time").val(), "固件生成时间", "time");
  if (err_msg != "") {
  $("#err_upadte_msg").html(err_msg);
  return false;
  }
  
  err_msg = checkInputStr($("#update_author").val(), "作者");
  if (err_msg != "") {
  $("#err_upadte_msg").html(err_msg);
  return false;
  }
  err_msg = checkInputStr($("#update_ReleaseNotes_download").val(), "ReleaseNotes地址");
  if (err_msg != "") {
    $("#err_upadte_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#update_build_download").val(), "固件地址");
  if (err_msg != "") {
    $("#err_upadte_msg").html(err_msg);
    return false;
  }
  
  let startstr = /^http/;
  if(startstr.test($("#update_build_download").val())){
    $("#err_upadte_msg").html("固件地址输入格式错误");
    return false;
  }else if(/\\/g.test($("#update_build_download").val())){
    $("#err_upadte_msg").html("固件地址输入格式错误");
    return false;
  }

  let firmwareAddr = $("#update_build_address").html () + $("#update_build_download").val();
  
  $.ajax({
    type: "POST",
    url: "updateNote.do",
    data: {
      "swVersion": $("#update_swVersion").html(),
      "midware": $("#update_middleware").val(),
      "midwareDate": $("#update_middleware_time").val(),
      "chipsetDate": $("#update_rk_time").val(),
      "firmwareDate": $("#update_build_time").val(),
      "author": $("#update_author").val(),
      "noteAddr": $("#update_ReleaseNotes_download").val(),
      "firmwareAddr":firmwareAddr
    },
    async: false,
    success: function (data) {
      if (data) {
        $("#error_msg").text("修改成功！");
        $("#error_box").show();
        $("#update_modal").hide();
        getDataModel();
      } else {
        $("#error_msg").text("修改失败！");
        $("#error_box").show();
        $("#update_modal").show();
      }
      clearTimer();
    }
  });

});
$("#cancelupdate").on('click', function () {
  $("#update_modal").hide();
  $("#update_swVersion").val("");
  $("#err_upadte_msg").html("");
  $("#update_ReleaseNotes_download").val("");
  $("#update_build_download").val("");
});

function clearTimer() {
  timer = setTimeout(function () {
    $("#error_box").hide();
  }, 1000);
}
//清空表格
function clearTable(tableid) {
  if ($(tableid).hasClass('dataTable')) {
    var dttable = $(tableid).dataTable();
    dttable.fnClearTable(); //清空一下table
    dttable.fnDestroy(); //还原初始化了的datatable
  };
  $(tableid).empty();
}
/*画表格模块*/

/*分页模块*/
function pageModel(total, rows) {
  $('.m-style').pagination({
    totalData: total, //数据总条数
    pageCount: Math.ceil(total / rows), //总页数
    showData: rows, //每页显示的条数
    mode: 'fixed', //模式，unfixed不固定页码按钮数量，fixed固定数量
    //count:1,//mode为unfixed时显示当前选中页前后页数，mode为fixed显示页码总数
    coping: true, //是否开启首页和末页，值为boolean
    isHide: true, //总页数为0或1时隐藏分页控件
    homePage: '首页',
    endPage: '末页',
    prevContent: '上页',
    nextContent: '下页',
    jump: true, //是否开启跳转到指定页数，值为boolean类型
    callback: function (api) {
      var searchData = {
        "productClass": $('#product').val(),
        "province": $('#province').val(),
        "offset": api.getCurrent() * rows - rows,
        "midware": $('#middleware').val(),
        "chipset": $('#chip').val(),
        "rows": $('#table1_length').val(),
        "operator": $('#operator').val(),
        "orderBy": $('#ordertype').val()
      }

      $.ajax({
        type: 'POST',
        url: "querySomeNotes.do",
        data: searchData,
        async: false,
        success: function (data) {
          dataset = creatTableData(data.notes);
          total = data.Total;
          rows = data.rows;
          $('#table1_info').text("共 " + data.Total + " 条数据，每页显示 " + data.rows + " 条，共 " + Math.ceil(total / rows) + " 页");
          drawTable(dataset);
        }
      });
    }
  });
}

/*分页模块*/

/*登出模块*/
//退出登录
$("#signOutButton").on('click', function () {
  $("#signout").show();
});
//登出操作
$("#signOutBtn").on('click', function () {
  $.ajax({
    type: 'post',
    url: "logout",
    success: function (data) {
      if (data.result) {
        $("#loginName").text("");
        $("#signOutButton").hide();
        $('#loginButton').show();
        $("#signout").hide();
        $("#AddBtn").hide();
        drawTable(dataset);
      }
    }
  });

});
//取消登出操作
$("#cancelSignOut").on('click', function () {
  $("#signout").hide();
  $("#AddBtn").show();
});
/*登出模块*/

/*登录模块*/
//登录
$("#loginButton").on('click', function () {
  $("#username").val("");
  $("#password").val("");
  $("#signup").show();
});
//登录操作
$("#signUpBtn").on('click', function () {
  let username = $("#username").val();
  let password = $("#password").val();
  if (username != '' && password != '') {
    var signData = {
      username: username,
      password: password
    }
    $.ajax({
      type: 'post',
      url: "login.do",
      data: signData,
      async: false,
      success: function (data) {
        afterShow(data.result, username);
      }
    });
  } else {
    $("#error_msg").text("请填写用户名或密码！");
    $("#error_box").show();
    clearTimer();
  }
});
//取消登录
$("#cancelSignup").on('click', function () {
  $("#signup").hide();
});


//登录请求结果显示
function afterShow(signup, username) {
  if (signup) { //true 为登录成功，隐藏signup model 反之登录失败，显示signup model 
    $("#signup").hide();
    $("#error_msg").text("登录成功！");
    $("#error_box").show();
    clearTimer();
    $("#loginName").text("欢迎：" + username);
    $("#signOutButton").show();
    $('#loginButton').hide();
    $("#AddBtn").show();
    drawTable(dataset);
  } else {
    $("#signup").show();
    $("#error_msg").text("登录失败！");
    $("#error_box").show();
    clearTimer();
    $("#loginButton").text("登录");
    $("#signOutButton").hide();
    $("#AddBtn").hide();
  }
}
/*登录模块*/

/*筛选模块*/
$('#table1_length').on("change", function () {
  getDataModel();
});
$('#onSearchData').on("click", function () {
  getDataModel();
});

/*请求接口*/
function getDataModel() {
  var searchData = {
    "productClass": $('#product').val(),
    "province": $('#province').val(),
    "offset": 0,
    "midware": $('#middleware').val(),
    "chipset": $('#chip').val(),
    "rows": $('#table1_length').val(),
    "operator": $('#operator').val(),
    "orderBy": $('#ordertype').val()
  }

  $.ajax({
    type: 'POST',
    url: "querySomeNotes.do",
    data: searchData,
    async: false,
    success: function (data) {
      dataset = creatTableData(data.notes);
      total = data.Total;
      rows = data.rows;
      $('#table1_info').text("共 " + data.Total + " 条数据，每页显示 " + data.rows + " 条，共 " + Math.ceil(total / rows) + " 页");
      drawTable(dataset);
      pageModel(total, rows);
    }
  });
}
/*筛选模块*/

/*添加release模块 */
$("#AddBtn").on('click', function () {
  $.ajax({
    type: "POST",
    url: "getLoginStatus.do",
    async: false,
    success: function (data) {
      if (data.username != "") {
        add_init();
        $("#add_Release").show();
      } else {
        $("#loginName").text("");
        $("#signOutButton").hide();
        $('#loginButton').show();
        $("#AddBtn").hide();
        $("#add_Release").hide();
        $("#error_msg").text("请重新登录！");
        $("#error_box").show();
        clearTimer();
      }
    }
  });

});
$("#cancelAddBtn").on('click', function () {
  $("#add_Release").hide();
});
$("#add_middleware").on("change",function(){
  if($("#add_middleware").val() == "noMidware"){
    $("#add_middleware_time").prop("disabled",true);
    $("#add_middleware_time").val("");
  }else{
    $("#add_middleware_time").prop("disabled",false);
  }
});
$("#add_Btn").on('click', function () {
  var res = checkAllInput();
  if (res) {
    $("#err_msg").html("");
    var addcheckData = {
      "swVersion": $("#add_swVersion").val(),
      "productClass": $("#add_product").val(),
      "wifiType": $("#add_wifi").val(),
      "operator": $("#add_operator").val(),
      "province": $("#add_province").val(),
      "chipset": $("#add_chip").val(),
      "midware": $("#add_middleware").val()
    };
    let firmwareAddr = $("#build_address").html () + $("#add_build_download").val();

    var addData = {
      "swVersion": $("#add_swVersion").val(),
      "productClass": $("#add_product").val(),
      "wifiType": $("#add_wifi").val(),
      "operator": $("#add_operator").val(),
      "province": $("#add_province").val(),
      "chipset": $("#add_chip").val(),
      "chipsetDate": $("#add_rk_time").val(),
      "midware": $("#add_middleware").val(),
      "midwareDate": $("#add_middleware_time").val(),
      "author": $("#add_author").val(),
      "firmwareDate": $("#add_build_time").val(),
      "noteAddr": $("#add_ReleaseNotes_download").val(),
      "firmwareAddr": firmwareAddr
    };

    $.ajax({
      type: 'POST',
      url: "verifyNote.do",
      data: addcheckData,
      async: false,
      success: function (data) {
        if (data && data.result == "OK") {
          $("#err_msg").html("");
          $.ajax({
            type: 'POST',
            url: "addNote.do",
            data: addData,
            async: false,
            success: function (data) {
              if (data.result) {
                $("#add_Release").hide();
                $("#error_msg").text("添加成功！");
                $("#error_box").show();
                clearTimer();
                $("#err_msg").html("");
                getDataModel();
              } else {
                $("#err_msg").html("Error：添加失败！");
              }

            }
          });
        } else {
          if (data && data.reason) {
            $("#err_msg").html("Error：" + data.reason);
          } else {
            $("#err_msg").html("Error：校验失败");
          }

        }
      }
    });



  }
});

function add_init() {
  $("#add_swVersion").val("");
  $("#add_product").val("");
  $("#add_operator").val("");
  $("#add_province").val("");
  $("#add_wifi").val("");
  $("#add_chip").val("");
  $("#add_rk_time").val("");
  $("#add_middleware").val("");
  $("#add_middleware_time").val("");
  $("#add_build_time").val("");
  $("#add_ReleaseNotes_download").val("");
  $("#add_build_download").val("");
  $("#add_author").val("");
  $("#err_msg").html("");
}

//输入校验
function checkInputStr(str, msg, type) {
  var errstr = '';
  if (str == "") {
    errstr = '请填写' + msg;
    return errstr;
  }

  if (/ /g.test(str)) {
    errstr = msg + '不能有空格！';
    return errstr;
  }

  if (type == "time") {
    var reg = /^\d+$/;
    if (!reg.test(str) && str != '') {
      errstr = msg + "中输入的字符必须是数字！";
    } else if (str.length != 8) {
      errstr = msg + "必须为8位！例：20180101 ";
    }
  }
  return errstr;
}

function checkAllInput() {
  let err_msg = '';
  err_msg = checkInputStr($("#add_swVersion").val(), "版本号");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_province").val(), "省份");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_operator").val(), "运营商");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_product").val(), "产品号");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_wifi").val(), "WiFi类型");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_chip").val(), "芯片规格");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_rk_time").val(), "芯片输入时间", "time");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_middleware").val(), "中间件");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }

  if($("#add_middleware").val() != "noMidware"){
    err_msg = checkInputStr($("#add_middleware_time").val(), "中间件输入时间", "time");
    if (err_msg != "") {
      $("#err_msg").html(err_msg);
      return false;
    }
  }

  err_msg = checkInputStr($("#add_build_time").val(), "固件生成时间", "time");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_author").val(), "作者");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_ReleaseNotes_download").val(), "ReleaseNotes地址");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }
  err_msg = checkInputStr($("#add_build_download").val(), "固件地址");
  if (err_msg != "") {
    $("#err_msg").html(err_msg);
    return false;
  }

  let startstr = /^http/;
  
  if(startstr.test($("#add_build_download").val())){
    $("#err_msg").html("固件地址输入格式错误");
    return false;
  }else if(/\\/g.test($("#add_build_download").val())){
    $("#err_msg").html("固件地址输入格式错误");
    return false;
  }

  return true;

}