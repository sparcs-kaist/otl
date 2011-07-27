/*
 * Online Timeplanner with Lectures
 * 2009 Spring CS408 Capstone Project
 *
 * OTL Timetable Javascript Implementation
 * depends on: jQuery 1.4.2, OTL Javascript Common Library
 */

/* Example of a lecture item.
Data.Lectures = 
[
	{
		id:'1',
		dept_id:'3847',
		classification:'기초필수',
		course_no:'CS202',
		class:'A',
		code:'37.231',
		title:'데이타구조',
		lec_time:'2',
		lab_time:'3',
		credit:'3',
		prof:'김민우',
		times:[{day:'화',start:480,end:600},{day:'수',start:480,end:600}],
		classroom:'창의학습관 304',
		limit:'200',
		num_people:'47',
		remarks:'영어강의',
		examtime:{day:'화,start:480,end:630}
	}
];
*/
function roundD(n, digits) {
	if (digits >= 0) return parseFloat(n.toFixed(digits));
	digits = Math.pow(10, digits);
	var t = Math.round(n * digits) / digits;
	return parseFloat(t.toFixed(0));
}

var NUM_ITEMS_PER_LIST = 15;
var NUMBER_OF_TABS = 3;
var Data = {};
var Mootabs = function(tabContainer, contents, trigerEvent, useAsTimetable)
	{
		if (trigerEvent==undefined) trigerEvent = 'mouseover';
		this.data = [];
		this.is_timetable = useAsTimetable ? true : false;

		this.tabs = $(tabContainer).children();
		this.contents = $(contents).children();
		$.each(this.tabs, $.proxy(function(index, item) {
			if (this.is_timetable)
				Data.Timetables[index] = {credit:0, au:0};
			$(item).bind(trigerEvent, $.proxy(function() {
				this.activate(index);
			}, this));
		}, this));
		$.each(this.contents, function(index, item)
		{
			$(item).addClass('none');
		});
		this.activate(0);
	};
Mootabs.prototype.setData = function(index,data)
	{
		this.data[index] = data;
	};
Mootabs.prototype.updateData = function()
	{
		if (this.is_timetable) {
			$('#total_credit').text(Data.Timetables[this.activeKey].credit);
			$('#total_au').text(Data.Timetables[this.activeKey].au);
			$('total_credit').highlight('#FFFF00');
			$('total_au').highlight('#FFFF00');
			$('#action-print').attr('href', '/timetable/print/?id=' + this.activeKey + '&view_year=' + Data.ViewYear + '&view_semester=' + Data.ViewTerm);
		}
	};
Mootabs.prototype.activate = function(key)
	{
		$.each(this.tabs, function(index, item)
		{
			if (index==key)
				$(item).addClass('active');
			else
				$(item).removeClass('active');
		});
		$.each(this.contents, function(index, item)
		{
			if (index==key) $(item).removeClass('none');
			else $(item).addClass('none');
		});
		this.activeKey = key;
		this.updateData();
	};
Mootabs.prototype.cleanTab = function(key)
	{
		$(this.contents[key]).empty();
	};
Mootabs.prototype.cleanActiveTab = function()
	{
		$(this.contents[this.activeKey]).empty();
	};
Mootabs.prototype.getActiveTab = function()
	{
		return this.contents[this.activeKey];
	};
Mootabs.prototype.getTabByKey = function(key)
	{
		return this.contents[key];
	};
Mootabs.prototype.getTableId = function()
	{
		return this.activeKey;
	};

var Utils = {
	days: ['월','화','수','목','금'],
	days_en: ['Mon.','Tue.','Wed.','Thu.','Fri.'],
	modulecolors:
		['#FFC7FE','#FFCECE','#DFE8F3','#D1E9FF','#D2F1EE','#FFEAD1','#E1D1FF','#FAFFC1','#D4FFC1','#DEDEDE','#BDBDBD'],
	modulecolors_highlighted:
		['#feb1fd','#ffb5b5','#c9dcf2','#b7dbfd','#b5f1eb','#fbd8ae','#d4bdfd','#f1f89f','#b9f2a0','#cbc7c7','#aca6a6'],
	getRandomColor: function()
	{
		return Utils.modulecolors[Math.floor(Math.random()*10)];
	},
	getColorByIndex: function(index)
	{
		//index =index*3;
		//index = Utils.modulecolors.length % index;
		return index % Utils.modulecolors.length;
	},
	mousePos: function(ev, wrap)
	{
		return {
			x: ev.pageX - $(wrap).offset().left,
			y: ev.pageY - $(wrap).offset().top
		};
	},
	clickable: function(o)
	{
		$(o).bind('mousedown',function(){ $(o).addClass('clicked') });
		$(document).bind('mouseup',function(){ $(o).removeClass('clicked') });
	},
	NumericTimeToReadable: function(t)
	{
		var hour = Math.floor(t / 60);
		var minute = t % 60;
		return (hour < 10 ? '0':'') + hour + ':' + (minute < 10 ? '0':'') + minute;
	}
};

var Map = {
	initialize:function()
	{
		this.container = $('#map-drag-container');
		this.dragmap = $('#dragmap');
		this.maptext= $('#map-text');
		this.settings = 
		{
			cW:$(this.container).innerWidth(),
			cH:$(this.container).innerHeight(),
			dW:$(this.dragmap).innerWidth(),
			dH:$(this.dragmap).innerHeight()
		}

		this.dragging = false;
		this.clickPos = null;

		this.dragmap.css('left',-258);
		this.dragmap.css('top',-270);
		this.registerHandlers();
		// The below is Mootools extension.
		Number.prototype.limit = function(min, max) {
			if (this < min) return min;
			else if (this > max) return max;
			else return this;
		};
	},
	registerHandlers:function()
	{
		this.dragHandler = $.proxy(this.onDrag, this);
		this.dragEndHandler = $.proxy(this.onEnd, this);
		$(this.dragmap).bind('mousedown',$.proxy(this.onMousedown, this));
	},
	onMousedown:function(ev)
	{
		this.dragging=true;
		$(document).bind('mousemove.map', this.dragHandler);
		$(document).bind('mouseup.map', this.dragEndHandler);
		this.clickPos = Utils.mousePos(ev, this.dragmap);
		ev.stopPropagation();
	},
	onDrag:function(e)
	{
		if (this.dragging)
		{
			var pos = Utils.mousePos(e,this.container);
			pos.x-=this.clickPos.x;
			pos.y-=this.clickPos.y;

			var s = this.settings;
			var left = (pos.x).limit((s.cW-s.dW+2), 0);
			var top = (pos.y).limit((s.cH-s.dH+2), 0);
			this.dragmap.css({
				'left': left+'px',
				'top': top+'px'
			});
			this.previous_target = null;

			e.stopPropagation();
		}
	},
	onEnd:function(e)
	{
		$(document).unbind('mousemove.map');
		$(document).unbind('mouseup.map');
		if (this.dragging)
		{
			this.dragging=false;
			e.stopPropagation();
		}
	},
	move:function(x,y)
	{
		var s = this.settings;

		x-=(s.cW/2);
		y-=(s.cH/2);

		var left = (x).limit(0, s.dW-s.cW);
		var top = (y).limit(0, s.dH-s.cH);
		this.dragmap.stop(true).animate({
			'left': (-left),
			'top':(-top)
		}, 250, 'easeInOutQuad');
	},
	find:function(name)
	{
		var arr = $.grep(Data.Map, function(item)
		{
			return item.name==name;
		});
		if (arr.length==0) return;

		var item = arr[0];
		var x = item.x;
		var y = item.y;
		$(this.maptext).css({'left': (x-6)+'px', 'top':(y-60)+'px'});
		$('#map-name').text(item.code+' '+item.name);
		if (this.previous_target != item.name)
			this.move(x,y);
		this.previous_target = item.name;
	}
};

var LectureList = {
	initialize:function(tabs,contents)
	{
		this.tabs = $('#lecture_tabs');
		this.contents = $('#lecture_contents');
		this.data = Data.Lectures;
		this.dept = $('#department');
		this.classf = $('#classification');
		this.keyword = $('#keyword');
		this.apply = $('#apply');

		this.loading = true;
		this.dept.selectedIndex = 0;
		this.registerHandles();
		this.onClassChange();
	},
	registerHandles:function()
	{
		$(this.dept).bind('change', $.proxy(this.onClassChange, this));
		$(this.classf).bind('change', $.proxy(this.onClassChange, this));
		$(this.apply).bind('click', $.proxy(this.onChange, this));
		$(this.keyword).bind('keypress', $.proxy(function(e) { if(e.keyCode == 13) { this.onChange(); }}, this));
	},
	getAutocompleteList:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		$.ajax({
			type: 'GET',
			url: '/timetable/autocomplete/',
			data: {'year': Data.ViewYear, 'term': Data.ViewTerm, 'dept': dept, 'type': classification, 'lang': USER_LANGUAGE},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					this.keyword.flushCache();
					this.keyword.autocomplete(resObj, {
						matchContains: true,
						scroll: true,
						width: 197,
						selectFirst: false
					});
				} catch(e) {
				}
			}, this),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
			}, this)
		});
	},
	onClassChange:function()
	{
		this.getAutocompleteList();
		this.onChange();
	},
	onChange:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		//TODO: classification을 언어와 상관 없도록 고쳐야 함
		if (dept == '-1' && USER_LANGUAGE == 'ko' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('키워드 없이 학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else if (dept == '-1' && USER_LANGUAGE == 'en' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('You must select a course type if you want to see \'ALL\' departments without keywords.');
		else
			this.filter({'dept':dept,'type':classification,'lang':USER_LANGUAGE,'keyword':keyword});
	},
	clearList:function()
	{
		LectureList.contents.empty(); 
		LectureList.buildTabs(LectureList.contents.children().length);
	},
	addToListMultiple:function(obj)
	{
		LectureList.contents.empty(); 
		var max = NUM_ITEMS_PER_LIST;
		var count=0;
		var content = $('<div>', {'class': 'lecture_content'});
		content.appendTo(LectureList.contents);
		var currCategory;
		$.each(obj, function(index, item) {
			var key = item.classification;
			if (currCategory != key) {
				currCategory = key;
				if (count < max) $('<h4>').text(currCategory).appendTo(content);
			}

			if (count>=max) {
				content = $('<div>', {'class':'lecture_content'}).appendTo(LectureList.contents);
				$('<h4>').text(currCategory).appendTo(content);
				count=0;
			} else
				count++;

			var el = $('<a>').text(item.title).appendTo(content);
			Utils.clickable(el);

			Data.CompRates[''+Data.ViewYear+Data.ViewTerm+item.course_no+item.class] = roundD(item.num_people / item.limit, 2)+' ( '+item.num_people+'/'+item.limit+' )';
			
			el.bind('mousedown', $.proxyWithArgs(Timetable.addLecture, Timetable, item));
			el.bind('mouseover', $.proxyWithArgs(Timetable.onMouseoverTemp, Timetable, item));
			el.bind('mouseout', $.proxyWithArgs(Timetable.onMouseout, Timetable, item));
		});
		LectureList.buildTabs(LectureList.contents.children().length);
		new Mootabs($('#lecture_tabs'), $('#lecture_contents'));
	},
	filter:function(conditions)
	{
		//TODO: conditions.type와 상관 없도록 고쳐야 함
		if (conditions.type == undefined){
			conditions.type = '전체보기';
		}
		if (conditions.year == undefined)
			conditions.year = Data.ViewYear;
		if (conditions.term == undefined)
			conditions.term = Data.ViewTerm;
		$.ajax({
			type: 'GET',
			url: '/timetable/search/',
			data: conditions,
			dataType: 'json',
			beforeSend: $.proxy(function() {
				if (this.loading)
					Notifier.showIndicator();
				else
					Notifier.setLoadingMsg(gettext('검색 중입니다...'));
			}, this),
			success: $.proxy(function(resObj) {
				try {
					if (resObj.length == 0) {
						LectureList.clearList();
						if (!this.loading)
							Notifier.setErrorMsg(gettext('과목 정보를 찾지 못했습니다.'));
					} else {
						LectureList.addToListMultiple(resObj);
						if (!this.loading)
							Notifier.setMsg(gettext('검색 결과를 확인하세요.'));
					}
				} catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
				if (this.loading)
					Notifier.clearIndicator();
				this.loading = false;
			}, this),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
				Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				this.loading = false;
			}, this)
		});
	},
	buildTabs:function(n)
	{
		this.tabs.empty();
		for (var i=1;i<=n;i++) {
			var tab = $('<div>',{'class':'lecture_tab'});
			$('<div>').text(i).appendTo(tab);
			tab.appendTo(this.tabs);
		}
	},
	getCategories:function(arr,category) // currently unused
	{
		var categories = [];
		/*
		$.each(arr, function(index, item) {
			var key = item.category;
			if (!categories.contains(key))
				categories.push(key);
		});
		*/
		return categories;
	},
	clustering:function(arr,category) // currently unused
	{
		var categories = this.getCategories(arr,category);
		var ret = [];
		/*
		categories.each(function(key)
		{
			arr.each(function(item){ 
				if($H(item).get(category)==key) ret.push(item) 
			});
		});
		*/
		return ret;
	}
};

var RangeSearch = {
	initialize:function()
	{
		this.grid = $('#grid');
		this.overlap = $('#overlap_modules');
		this.overlap.css('display','none');

		this.dragging=false;
		this.startCell = {row:0,col:0};

		this.options = {
			cellHeight:21,
			cellWidth:100
		};
		this.selection=$('#cellselected');
		this.selection.css('display','none');

		this.registerHandlers();
	},
	registerHandlers:function()
	{
		this.dragHandler = $.proxy(this.onDrag, this);
		this.dragEndHandler = $.proxy(this.onEnd, this);
		this.grid.bind('mousedown', $.proxy(this.onMousedown, this));
	},
	onMousedown:function(e)
	{
		this.dragging=true;
		$(document).bind('mousemove.rangesearch', this.dragHandler);
		$(document).bind('mouseup.rangesearch', this.dragEndHandler);
		var pos = Utils.mousePos(e,this.grid);
		this.startCell = this.getCell(pos);

		var x = (this.startCell.col * this.options.cellWidth)+1;
		var y = (this.startCell.row * this.options.cellHeight);
		$(this.selection).css(
			{
				display:'block',
				left:x,
				top:y,
				width:this.options.cellWidth,
				height:this.options.cellHeight
			}
		);
		e.stopPropagation();
	},
	onDrag:function(e)
	{
		if(this.dragging)
		{
			var pos = Utils.mousePos(e,this.grid);
			var currentCell = this.getCell(pos);
			var cell = this.modCell(this.startCell,currentCell);
			this.draw(cell.c1,cell.r1,cell.c2,cell.r2);
			e.stopPropagation();
		}
	},
	onEnd:function(e)
	{
		$(document).unbind('mousemove.rangesearch');
		$(document).unbind('mouseup.rangesearch');
		if(this.dragging)
		{
			var pos = Utils.mousePos(e,this.grid);
			var endCell = this.getCell(pos);
			$(this.selection).css('display','none');
			var cell = this.modCell(this.startCell,endCell);

			var startDay = cell.c1;
			var endDay = cell.c2;
			var startTime = cell.r1*30+480;
			var endTime = cell.r2*30+510;
			if (endTime - startTime == 30) {
				Notifier.setMsg(gettext('드래그해서 1시간 이상의 영역을 선택하시면 보다 정확한 범위 검색을 하실 수 있습니다.'));
				return;
			}

			this.dragging=false;
			$('#lecturelist-filter').css('display','none');
			var dayRange = '';
			if (startDay == endDay){
				//TODO: 요일표시를 어떻게 하면 좋을까... 부터 시작해서 여기가 지뢰밭이네
				if (USER_LANGUAGE == 'en')
					dayRange = Utils.days_en[startDay];
				else
					dayRange = Utils.days[startDay]+'요일';
			}
			else{
				// TODO-check: js에서 맞는 문법인 지 잘 모르겠음
				if (USER_LANGUAGE == 'en')
					dayRange = 'From '+Utils.days_en[startDay]+' to '+Utils.days_en[endDay];
				else
					dayRange = Utils.days[startDay]+'요일부터 '+Utils.days[endDay]+'요일까지';
			}
			if (USER_LANGUAGE == 'en')
				$('#lecturelist-range').html('<h4>Range search</h4><p>'+dayRange+'<br/>' + 
					'From '+Utils.NumericTimeToReadable(startTime)+' to '+Utils.NumericTimeToReadable(endTime)+'</p>');
			else
				$('#lecturelist-range').html('<h4>범위 검색</h4><p>'+dayRange+'<br/>' + 
					Utils.NumericTimeToReadable(startTime)+'부터 '+Utils.NumericTimeToReadable(endTime)+'까지</p>');

			var buttonMessage='';
			buttonMessage = gettext('학과/구분/키워드 검색으로 돌아가기');
			$('<button>')
			.text(buttonMessage)
			.click(function() {
				$('#lecturelist-filter').css('display','block');
				$('#lecturelist-range').empty();
				LectureList.onChange();
			})
			.appendTo('#lecturelist-range')
			.attr('id', 'back_to_search');
			LectureList.filter({start_day:startDay, end_day:endDay, start_time:startTime, end_time:endTime});
		}
	},
	modCell:function(cell1,cell2)
	{
		return {
			c1 :Math.max(Math.min(cell1.col,cell2.col),0),
			r1 :Math.max(Math.min(cell1.row,cell2.row),0),
			c2 :Math.min(Math.max(cell1.col,cell2.col),4),
			r2 :Math.min(Math.max(cell1.row,cell2.row),31)
		};
	},
	draw:function(col1,row1,col2,row2)
	{
		var x = col1 * this.options.cellWidth + 1; // +1 fix
		var y = row1 * this.options.cellHeight;
		var width = (col2-col1+1) * this.options.cellWidth;
		var height = (row2-row1+1) * this.options.cellHeight;
		this.selection.css(
			{
				left:x,
				top:y,
				width:width,
				height:height
			}
		);
	},
	getCell:function(coords)
	{
		var row = Math.floor(coords.y/this.options.cellHeight);
		var col = Math.floor(coords.x/this.options.cellWidth);
		return {row:row,col:col};
	}
	
};

var Timetable = {
	initialize:function()
	{
		this.grid = $('#grid');
		this.overlap = $('#overlap_modules');
		this.overlap.css('display','none');
		this.tabs = new Mootabs($('#timetable_tabs'), $('#timetable_contents'), 'mousedown', true);
		this.onLoad();
		this.registerHandlers();
	},
	onLoad:function()
	{
		var initData = Data.MyLectures;
		var have_deleted = false;
		var deleted_list = '';
		$.each(initData, function(index, item) {
			var credit=0,au=0;
			var wrap = Timetable.tabs.getTabByKey(index);
			var deleted_count = 0;
			$.each(item, function(index, item) {
				credit += item.credit;
				au += item.au;
				var bgcolor = Utils.getColorByIndex(index);
				if (item.deleted) {
					deleted_list += (deleted_count==0 ? '' : ', ')+item.course_no+' '+item.title;
					have_deleted = true;
					deleted_count++;
				} else {
					Data.CompRates[''+Data.ViewYear+Data.ViewTerm+item.course_no+item.class] = roundD(item.num_people / item.limit, 2)+' ( '+item.num_people+'/'+item.limit+' )';
					Timetable.buildlmodules(wrap,item,bgcolor,true);
				}
			});
			Data.Timetables[index] = {credit:credit, au:au};
		});
		Timetable.tabs.updateData();
		if (have_deleted) {
			if (USER_LANGUAGE == 'en')
				Notifier.setErrorMsg('<strong>'+deleted_list+'</strong>, enrolled in your list, is cancelled.');
			else
				Notifier.setErrorMsg('추가하신 과목 중 <strong>'+deleted_list+'</strong>이(가) 폐강되었습니다.');
		}
	},
	registerHandlers:function()
	{
		$('#action-cleanTable').click($.proxyWithArgs(this.deleteLecture, this, null));
	},
	onMouseout:function()
	{
		$('#add_credit').empty();
		$('#add_au').empty();
		this.overlap.css('display','none');
	},
	addLecture:function(e,obj)
	{
		e.stopPropagation();
		var table_id = Timetable.tabs.getTableId();
		var lecture_id = obj.id;

		$.ajax({
			type: 'GET', 
			url: '/timetable/add/',
			data: {'table_id':table_id, 'lecture_id':lecture_id, 'view_year':Data.ViewYear, 'view_semester':Data.ViewTerm},
			dataType: 'json',
			beforeSend: function(xhr)
			{
				Notifier.setLoadingMsg(gettext('추가하는 중입니다...'));
			},
			success: $.proxy(function(resObj)
			{
				try {
					if (resObj.result=='OK') {
						Timetable.update(resObj);
						this.overlap.stop(true,true).animate({'opacity':0}, 200, 'linear');
						

						Notifier.setMsg('<strong>'+obj.title+'</strong> '+gettext('추가되었습니다.'));
					} else {
						var msg;
						switch(resObj.result)
						{
							case 'NOT_EXIST':
								msg = gettext('강의가 존재하지 않습니다.');
								break;
							case 'OVERLAPPED':
							case 'DUPLICATED':
								msg = gettext('강의 시간이 겹칩니다.');
								break;
							case 'ERROR':
							default:
								msg = gettext('기타 오류입니다.');
								break;
						}
						Notifier.setErrorMsg(msg);
					}
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if (xhr.status == 403){
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else{
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},
	deleteLecture:function(e,obj)
	{
		e.stopPropagation();
		var confirmMsg,sendData,successMsg, table_id = Timetable.tabs.getTableId();
		if (obj==null) 
		{
			confirmMsg = gettext('현재 예비 시간표를 초기화 하겠습니까?');
			sendData={'table_id':table_id, 'view_year':Data.ViewYear, 'view_semester':Data.ViewTerm};
			successMsg = gettext('예비 시간표가 <strong>초기화</strong> 되었습니다');
		}
		else
		{
			//TODO: interpolate 씌우기
			if (USER_LANGUAGE == 'en')
				confirmMsg='Do you want to delete "'+obj.title+'"?';
			else
				confirmMsg='"'+obj.title+'" 예비 시간표에서 삭제 하시겠습니까?';
			sendData={'table_id':table_id, 'lecture_id':obj.id, 'view_year':Data.ViewYear, 'view_semester':Data.ViewTerm};
			successMsg='<strong>'+obj.title+'</strong> '+gettext('삭제 되었습니다');
		}

		if(confirm(confirmMsg))
		{
			$.ajax({
				type: 'GET', 
				url: '/timetable/delete/',
				data: sendData,
				dataType: 'json',
				beforeSend: function() {
					Notifier.setLoadingMsg(gettext('삭제하는 중입니다...'));
				},
				success: function(resObj)
				{
					try {
						switch (resObj.result) {
						case 'OK':
							Timetable.update(resObj);
							Notifier.setMsg(successMsg);
							break;
						case 'NOT_EXIST':
							Notifier.setErrorMsg(gettext('해당 강의가 추가되어 있지 않습니다.'));
							break;
						default:
							Notifier.setErrorMsg(gettext('기타 오류입니다.'));
						}
					} catch(e) {
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
					}
				},
				error: function(xhr) {
					if (suppress_ajax_errors)
						return;
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			});
		}
	},
	changeSemester:function()
	{
		$.ajax({
			type: 'GET',
			url: '/timetable/change/',
			data: {'view_year': Data.ViewYear, 'view_semester': Data.ViewTerm},
			dataType: 'json',
			beforeSend: $.proxy(function() {
				Notifier.showIndicatorSemester();
			}, this),
			success: $.proxy(function(resObj) {
				try {
					Data.MyLectures = resObj.data
					var key;
					for(key=0;key<NUMBER_OF_TABS;key++) {
						Timetable.updateTab({'data': Data.MyLectures[key]}, key);
					}
				} catch(e) {
				}
				Notifier.clearIndicatorSemester();
			}, this),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
			}, this)
		});
	},
	update:function(resObj)
	{
		var credit=0,au=0;
		Timetable.tabs.cleanActiveTab();
		$.each(resObj.data, function(index,item) {
			credit += item.credit;
			au += item.au;
			var bgcolor = Utils.getColorByIndex(index);
			Data.CompRates[''+Data.ViewYear+Data.ViewTerm+item.course_no+item.class] = roundD(item.num_people / item.limit, 2)+' ( '+item.num_people+'/'+item.limit+' )';
			Timetable.buildlmodules(Timetable.tabs.getActiveTab(), item, bgcolor, true);
		});
		
		Data.Timetables[Timetable.tabs.getTableId()] = {credit:credit,au:au};
		Timetable.tabs.updateData();
	},
	updateTab:function(resObj, key)
	{
		var credit=0,au=0;
		Timetable.tabs.cleanTab(key);
		$.each(resObj.data, function(index,item) {
			credit += item.credit;
			au += item.au;
			var bgcolor = Utils.getColorByIndex(index);
			Data.CompRates[''+Data.ViewYear+Data.ViewTerm+item.course_no+item.class] = roundD(item.num_people / item.limit, 2)+' ( '+item.num_people+'/'+item.limit+' )';
			Timetable.buildlmodules(Timetable.tabs.getTabByKey(key), item, bgcolor, true);
		});

		Data.Timetables[key] = {credit:credit,au:au};
		Timetable.tabs.updateData();
	},
	getCompRate:function(obj)
	{
		var registerCompRateTmp = function(year, term, course_no, class) {
			var registerCompRate = function(resObj) {
				try {
					Data.CompRates[''+year+term+course_no+class] = roundD(resObj.num_people/resObj.limit, 2)+' ( '+resObj.num_people+'/'+resObj.limit+' )';
					if( year == Data.ViewYear && term == Data.ViewTerm && course_no == $('#DS_course_no').html() && class == $('#DS_class').html() ) {
						$('#DS_comp_rate').html(Data.CompRates[''+year+term+course_no+class]);
					}
				} catch(e) {
				}
			};
			return registerCompRate;
		};
		$.ajax({
			type: 'GET',
			url: '/timetable/comp_rate/',
			data: {'year': Data.ViewYear, 'term': Data.ViewTerm, 'course_no': obj['course_no'], 'class': obj['class']},
			dataType: 'json',
			success: registerCompRateTmp(Data.ViewYear, Data.ViewTerm, obj['course_no'], obj['class']),
			error: $.proxy(function(xhr) {
				if (suppress_ajax_errors)
					return;
			}, this)
		});
	},
	updateInfoPanel: function(obj, is_adding)
	{
		for (key in obj) {
			if ($('#DS_'+key)!=null || key=='au') {
				var item = obj[key];
				if (item!=null) {
					switch (key) {
					case 'examtime':
						var time = Utils.NumericTimeToReadable(item.start) + ' ~ ' + Utils.NumericTimeToReadable(item.end);
						var name_and_time = obj.title+' '+time;
						$('#DS_'+key).text(Utils.days[item.day]+time);
						//if (is_adding)
						//	$('add_examtime'+item.day).set('text', name_and_time);
						break;
					case 'credit':
						if (item > 0 && is_adding)
							$('#add_credit').text('(+'+item+')');
						$('#DS_'+key).text(item);
						break;
					case 'au':
						if (item > 0 && is_adding)
							$('#add_au').text('(+'+item+')');
						break;
					case 'title':
						link_url = 'https://cais.kaist.ac.kr/syllabusStud?year='+Data.ViewYear+'&term='+Data.ViewTerm+'&subject_no='+obj['code']+'&lecture_class='+obj['class']+'&dept_id='+obj['dept_id'];
						$('#DS_'+key).html('<p><a href="'+link_url+'" target="_blank"><img src="'+Data.MediaUrl+'images/syllabus.png" id="syllabus" title="'+gettext('실라버스')+'" alt="'+gettext('실라버스')+'" /></a> '+item+'</p>');
						break;
					case 'prof':
						$('#DS_'+key).html('<p>'+item+'</p>');
						break;
					case 'num_people':
						if( ''+Data.ViewYear+Data.ViewTerm+obj['course_no']+obj['class'] in Data.CompRates ) {
							$('#DS_comp_rate').html(Data.CompRates[''+Data.ViewYear+Data.ViewTerm+obj['course_no']+obj['class']]);
						}
						else {
							this.getCompRate(obj);
						}
						break;
					case 'limit':
						break;
					default:
						$('#DS_'+key).text(item);
					}
				}
			}
		}
		if (!obj['examtime'])
			$('#DS_examtime').text('');
	},
	onMouseoverTemp: function(ev, obj)
	{
		this.onMouseover(ev, obj, true);

		this.overlap.stop(true).empty().css('display','block');
		this.buildlmodules(this.overlap,obj,-1,false);
		this.overlap.css('opacity', 1.0);
	},
	onMouseover: function(ev, obj, is_adding)
	{
		this.updateInfoPanel(obj, is_adding);
		if (obj.classroom != undefined) {
			var tokens = obj.classroom.split(' ');
			var classroom = tokens.slice(0, tokens.length-1).join(' ');
			Map.find(classroom);
		}
	},
	buildlmodules:function(wrap,obj,bgcolor_index,enableDelete)
	{
		var is_first = true;

		$.each(obj.times, $.proxy(function(index, time)
		{
			var lmodule = $('<div>',{'class':'lmodule', 'id':obj.code});
			var bg = $('<div>',{'class':'bg'});
			var textbody = $('<div>',{'class':'textbody'});
			var bgcolor, bgcolor_highlighted;
			if (bgcolor_index == -1) {
				bgcolor = '#f93';
				bgcolor_highlighted = '#f48c39';
			} else {
				bgcolor = Utils.modulecolors[bgcolor_index];
				bgcolor_highlighted = '#ffd02b';
			}
			bg.appendTo(lmodule);
			textbody.appendTo(lmodule);
			if (enableDelete) {
				textbody.html('<a class="cursor"><strong>'+obj.title+'</strong></a><br />'+obj.prof+'<br />'+obj.classroom+'<br />');
				var deletelink = textbody.children('a');
				deletelink.bind('mousedown', function(ev) { ev.stopPropagation(); });
				deletelink.bind('click', $.proxyWithArgs(Timetable.deleteLecture, Timetable, obj)); 
			} else
				textbody.html('<strong>'+obj.title+'</strong><br />'+obj.prof+'<br />'+obj.classroom+'<br />');

			var left = time.day*100+3;
			var top = Math.floor((time.start-480)/30)*21;
			var height = Math.floor((time.end-time.start)/30)*21 - 2;

			bg.css({'background':bgcolor});

			if (enableDelete) {
				lmodule.bind('mouseover', $.proxyWithArgs(Timetable.onMouseover, Timetable, obj, false));

				// 같은 과목의 여러 lmodule 중 하나에만 마우스를 올려도 다함께 highlight되도록 하는 처리
				lmodule.bind('mouseover', function(ev) {
					$.each($('#timetable-item-'+obj.course_no+obj['class']).data('mymodules'), function(index, item) {
						$(item).children('.bg').css('background',bgcolor_highlighted);
					});
				});
				lmodule.bind('mouseout', function(ev) {
					$.each($('#timetable-item-'+obj.course_no+obj['class']).data('mymodules'), function(index, item) {
						$(item).children('.bg').css('background',bgcolor);
					});
				});
				// 처음 추가되는 lmodule 항목은 고유 ID를 가지며, 여기서 element storage를 이용해 자신과 다른 lmodule들의 reference를 저장한다.
				if (is_first) {
					lmodule.attr('id', 'timetable-item-'+obj.course_no+obj['class']);
					is_first = false;
				}
			}

			// DOM에 lmodule 삽입
			lmodule.css({'left':left,'top':top,'height':height});
			lmodule.appendTo(wrap);

			// 고유 ID를 가진 lmodule 항목에 reference 추가
			if (enableDelete) {
				var modules = $('#timetable-item-'+obj.course_no+obj['class']).data('mymodules') || [];
				modules.push(lmodule);
				$('#timetable-item-'+obj.course_no+obj['class']).data('mymodules', modules);
			}
		}, this));
	}
};
