/*
 * Online Timeplanner with Lectures
 * 2009 Spring CS408 Capstone Project
 *
 * OTL Timetable Javascript Implementation
 * depends on: Mootools 1.2, OTL Javascript Common Library
 */

/* Example of a lecture item.
Data.Lectures = 
[
	{
		id:'1',
		year:'2008',
		term:'3',
		dept:'전산학전공',
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
		fixed_num:'200',
		remarks:'영어강의',
		examtime:{day:'화,start:480,end:630}
	}
];
*/

var NUM_ITEMS_PER_LIST = 20;
var Data = {};
var Mootabs = new Class({
	initialize: function(tabs, contents, trigerEvent, useAsTimetable)
	{
		if (trigerEvent==undefined) trigerEvent = 'mouseover';
		this.data = [];
		this.is_timetable = useAsTimetable ? true : false;

		this.tabs = $(tabs).getChildren();
		this.contents = $(contents).getChildren();
		this.tabs.each(function(item,key) 
		{
			if (this.is_timetable)
				Data.Timetables[key] = {credit:0, au:0};
			item.addEvent(trigerEvent, function()
				{
					this.activate(key);
				}.bind(this)
			);
		}.bind(this));
		this.contents.each(function(item)
		{
			item.addClass('none');
		});

		this.activate(0);
	},
	setData:function(index,data)
	{
		this.data[index] = data;
	},
	updateData:function()
	{
		if (this.is_timetable) {
			$('total_credit').set('html', Data.Timetables[this.activeKey].credit);
			$('total_au').set('html', Data.Timetables[this.activeKey].au);
			$('total_credit').highlight('#FFFF00');
			$('total_au').highlight('#FFFF00');
		}
	},
	activate: function(key)
	{
		this.tabs.each(function(item,index)
		{
			if (index==key)
				item.addClass('active');
			else
				item.removeClass('active');
		});
		this.contents.each(function(item,index)
		{
			if (index==key) item.removeClass('none');
			else item.addClass('none');
		});
		this.activeKey = key;

		this.updateData();
	},
	cleanActiveTab:function()
	{
		this.contents[this.activeKey].empty();
	},
	getActiveTab:function()
	{
		return this.contents[this.activeKey];
	},
	getTabByKey:function(key)
	{
		return this.contents[key];
	},
	getTableId:function()
	{
		return this.activeKey;
	}
});

var UDF = {
	days: ['월','화','수','목','금'],
	modulecolors:
		['#FFC7FE','#FFCECE','#DFE8F3','#D1E9FF','#D2F1EE','#FFEAD1','#E1D1FF','#FAFFC1','#D4FFC1','#DEDEDE','#BDBDBD'],
	modulecolors_highlighted:
		['#feb1fd','#ffb5b5','#c9dcf2','#b7dbfd','#b5f1eb','#fbd8ae','#d4bdfd','#f1f89f','#b9f2a0','#cbc7c7','#aca6a6'],
	getRandomColor:function()
	{
		return UDF.modulecolors[Math.floor(Math.random()*10)];
	},
	getColorByIndex:function(index)
	{
		//index =index*3;
		//index = UDF.modulecolors.length % index;
		return index % UDF.modulecolors.length;
	},
	cumulativeOffset : function(el)
	{
		var valueT = 0, valueL = 0;
		do {
			valueT += el.offsetTop  || 0;
			valueL += el.offsetLeft || 0;
			el = el.offsetParent;
		} while (el);
		return {x:valueL,y:valueT};
	},
	mousePos:function(e, wrap)
	{
		var event =new Event(e);
		var pos= UDF.cumulativeOffset(wrap);
		return { 
			x:(event.page.x-pos.x),
			y:(event.page.y-pos.y)
		}
	},
	clickable : function(o)
	{
		o.addEvent('mousedown',function(){ o.addClass('clicked') });
		document.addEvent('mouseup',function(){ o.removeClass('clicked') });
	},
	NumericTimeToReadable: function(t)
	{
		var hour = Math.floor(t / 60);
		var minute = t % 60;
		return (hour < 10 ? '0':'') + hour + ':' + (minute < 10 ? '0':'') + minute;
	}
}

var LectureList = {
	initialize:function(tabs,contents)
	{
		this.tabs = $('lecture_tabs');
		this.contents = $('lecture_contents');
		this.data = $A(Data.Lectures);
		this.dept = $('department');
		this.classf= $('classification');

		this.dept.selectedIndex = 0;
		this.registHandles();
		this.onChange();
	},
	registHandles:function()
	{
		this.dept.addEvent('change',this.onChange.bind(this,'dept'));
		this.classf.addEvent('change',this.onChange.bind(this,'dept'));
	},
	onChange:function()
	{
		var dept = this.dept.options[this.dept.selectedIndex].value;
		var classification = this.classf.options[this.classf.selectedIndex].text;
		if (dept == '-1' && classification == '전체보기')
			Notifier.setErrorMsg('학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else
			this.filter({'dept':dept,'type':classification});
	},
	clearList:function()
	{
		LectureList.contents.empty(); 
		LectureList.buildTabs(LectureList.contents.getChildren().length);
	},
	addToListMultiple:function(obj)
	{
		LectureList.contents.empty(); 
		var max = NUM_ITEMS_PER_LIST;
		var count=0;
		var content = new Element('div',{'class':'lecture_content'}).inject(LectureList.contents);
		var currCategory;
		obj.each(function(item)
		{
			var key = item.classification;
			if (currCategory != key) {
				currCategory = key;
				if(count<max) new Element('h4',{'html':currCategory}).inject(content);
			}

			if (count>=max) {
				content = new Element('div',{'class':'lecture_content'}).inject(this.contents);
				new Element('h4',{'html':currCategory}).inject(content);
				count=0;
			} else
				count++;

			var el = new Element('a',{'html':item.title}).inject(content);
			UDF.clickable(el);
			
			el.addEvent('mousedown',Timetable.addLecture.bindWithEvent(Timetable,item));
			el.addEvent('mouseover',Timetable.onMouseoverTemp.bind(Timetable,item));
			el.addEvent('mouseout',Timetable.onMouseout.bind(Timetable,item));
		}.bind(LectureList));
		LectureList.buildTabs(LectureList.contents.getChildren().length);
		new Mootabs('lecture_tabs','lecture_contents');
	},
	filter:function(conditions)
	{
		if (conditions.type == undefined)
			conditions.type = '전체보기';
		var request = new Request({
			method:'get',
			url:'/timetable/search/',
			onRequest:function()
			{
				Notifier.setLoadingMsg('검색 중입니다...');
			},
			onSuccess:function(responseText)
			{
				try {
					var resObj = JSON.decode(responseText);
					if (resObj.length == 0) {

						LectureList.clearList();
						Notifier.setErrorMsg('과목 정보를 찾지 못했습니다.');

					} else {

						LectureList.addToListMultiple(resObj);
						Notifier.setMsg('검색 결과를 확인하세요.');
					}
				} catch(e) {
					Notifier.setErrorMsg('오류가 발생하였습니다. ('+e.message+')');
				}
			},
			onFailure:function(xhr)
			{
				Notifier.setErrorMsg('오류가 발생하였습니다. (요청 실패:'+xhr.status+')');
			}
		});
		query = '';
		if (conditions.year == undefined)
			conditions.year = Data.NextYear;
		if (conditions.term == undefined)
			conditions.term = Data.NextTerm;
		for (key in conditions) {
			query += key + '=' + encodeURIComponent(conditions[key]) + '&'
		}
		request.send(query);
	},
	buildTabs:function(n)
	{
		this.tabs.empty();
		for (var i=1;i<=n;i++)
			new Element('div',{'html':i}).inject(new Element('div',{'class':'lecture_tab'}).inject(this.tabs));
	},
	getCategories:function(arr,category) // currently unused
	{
		var categories = [];
		arr.each(function(item)
		{
			var key = $H(item).get(category);
			if (!categories.contains(key))
				categories.push(key);
		});
		return categories;
	},
	clustering:function(arr,category) // currently unused
	{
		var categories = this.getCategories(arr,category);
		var ret = [];
		categories.each(function(key)
		{
			arr.each(function(item){ 
				if($H(item).get(category)==key) ret.push(item) 
			});
		});
		return ret;
	}
};

var RangeSearch = {
	initialize:function()
	{
		this.grid = $('grid');
		this.overlap = $('overlap_modules');
		this.overlap.setStyle('display','none');

		this.dragging=false;
		this.startCell = {row:0,col:0};

		this.options=
		{
			cellHeight:21,
			cellWidth:100
		}
		this.selection=$('cellselected');
		this.selection.setStyle('display','none');

		this.registHandlers();
	},
	registHandlers:function()
	{
		this.dragHandler = this.onDrag.bindWithEvent(this);
		this.dragEndHandler = this.onEnd.bindWithEvent(this);
		this.grid.addEvent('mousedown',this.onMousedown.bindWithEvent(this));
	},
	onMousedown:function(e)
	{
		this.dragging=true;
		document.addEvent('mousemove', this.dragHandler);
		document.addEvent('mouseup', this.dragEndHandler);
		var pos = UDF.mousePos(e,this.grid);
		this.startCell = this.getCell(pos);

		var x = (this.startCell.col * this.options.cellWidth)+1;
		var y = (this.startCell.row * this.options.cellHeight);
		this.selection.setStyles(
			{
				display:'block',
				left:x,
				top:y,
				width:this.options.cellWidth,
				height:this.options.cellHeight
			}
		);
		e.stop();
	},
	onDrag:function(e)
	{
		if(this.dragging)
		{
			var pos = UDF.mousePos(e,this.grid);
			var currentCell = this.getCell(pos);
			var cell = this.modCell(this.startCell,currentCell);
			this.draw(cell.c1,cell.r1,cell.c2,cell.r2);
			e.stop();
		}
	},
	onEnd:function(e)
	{
		document.removeEvent('mousemove',this.dragHandler);
		document.removeEvent('mouseup',this.dragEndHandler);
		if(this.dragging)
		{
			var pos = UDF.mousePos(e,this.grid);
			var endCell = this.getCell(pos);
			this.selection.setStyle('display','none');
			var cell = this.modCell(this.startCell,endCell);

			var startDay = cell.c1;
			var endDay = cell.c2;
			var startTime = cell.r1*30+480;
			var endTime = cell.r2*30+510;
			if (endTime - startTime == 30) {
				Notifier.setMsg('드래그해서 1시간 이상의 영역을 선택하시면 보다 정확한 범위 검색을 하실 수 있습니다.');
				return;
			}

			this.dragging=false;
			$('lecturelist-filter').setStyle('display','none');
			var dayRange = '';
			if (startDay == endDay)
				dayRange = UDF.days[startDay]+'요일';
			else
				dayRange = UDF.days[startDay]+'요일부터 '+UDF.days[endDay]+'요일까지';
			$('lecturelist-range').set('html', '<h4>범위 검색</h4><p>'+dayRange+'<br/>' + 
				UDF.NumericTimeToReadable(startTime)+'부터 '+UDF.NumericTimeToReadable(endTime)+'까지</p>');

			var return_button = new Element('button', {'text':'학과/구분 검색으로 돌아가기'});
			return_button.addEvent('click', function() {
				$('lecturelist-filter').setStyle('display','block');
				$('lecturelist-range').set('html', '');
				var dept = LectureList.dept.options[LectureList.dept.selectedIndex].value;
				var classification = LectureList.classf.options[LectureList.classf.selectedIndex].text;
				LectureList.filter({dept:dept, type:classification});
			});
			$('lecturelist-range').appendChild(return_button);
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
		this.selection.setStyles(
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
		this.grid = $('grid');
		this.overlap = $('overlap_modules');
		this.overlap.setStyle('display','none');
		this.tabs = new Mootabs('timetable_tabs','timetable_contents','mousedown', true);
		this.onLoad();
		this.registHandlers();
	},
	onLoad:function()
	{
		var initData = Data.MyLectures;
		var have_deleted = false;
		var deleted_list = '';
		initData.each(function(arr, key)
		{
			var credit=0,au=0;
			var wrap = Timetable.tabs.getTabByKey(key);
			var deleted_count = 0;
			arr.each(function(obj, index)
			{
				credit += obj.credit;
				au += obj.au;
				var bgcolor = UDF.getColorByIndex(index);
				if (obj.deleted) {
					deleted_list += (deleted_count==0 ? '' : ', ')+obj.course_no+' '+obj.title;
					have_deleted = true;
					deleted_count++;
				} else
					Timetable.buildlmodules(wrap,obj,bgcolor,true);
			});
			Data.Timetables[key] = {credit:credit,au:au};
		});
		Timetable.tabs.updateData();
		if (have_deleted) {
			Notifier.setErrorMsg('추가하신 과목 중 <strong>'+deleted_list+'</strong>이(가) 폐강되었습니다.');
		}
	},
	registHandlers:function()
	{
		$('action-cleanTable').addEvent('click',this.deleteLecture.bindWithEvent(this,null));
		$('action-print').addEvent('click',this.print.bindWithEvent(this));
	},
	print:function()
	{
		Notifier.setErrorMsg('아직 구현되지 않았습니다. =3');
	},
	onMouseout:function()
	{
		$('add_credit').empty();
		$('add_au').empty();
		this.overlap.setStyle('display','none');
	},
	addLecture:function(e,obj)
	{
		e.stop();
		var table_id = Timetable.tabs.getTableId();
		var lecture_id = obj.id;

		var myRequest = new Request({
			method: 'get', 
			url: '/timetable/add/',
			onRequest:function()
			{
				Notifier.setLoadingMsg('추가하는 중입니다...');
			},
			onSuccess:function(responseText)
			{
				try{
					var resObj = JSON.decode(responseText);
					if (resObj.result=='OK')
					{
						Timetable.update(resObj);
						Timetable.overlap.fade('out');
						
						Notifier.setMsg('<strong>'+obj.title+'</strong> 추가 되었습니다');
					}
					else
					{
						var msg;
						switch(resObj.result)
						{
							case 'NOT_EXIST':
								msg='강의가 존재하지 않습니다.' ;
								break;
							case 'OVERLAPPED':
							case 'DUPLICATED':
								msg='강의 시간이 겹칩니다.';
								break;
							case 'ERROR':
							default:
								msg = '기타 오류입니다.';
								break;
						}
						Notifier.setErrorMsg(msg);
					}
				}
				catch(e)
				{
					Notifier.setErrorMsg('오류가 발생하였습니다. ('+e.message+')');
				}
			},
			onFailure:function(xhr) {
				if (xhr.status == 403)
					Notifier.setErrorMsg('로그인해야 합니다.');
				else
					Notifier.setErrorMsg('오류가 발생하였습니다. (요청 실패:'+xhr.status+')');
			}
		});
		myRequest.send('table_id='+table_id+'&lecture_id='+lecture_id);
	},
	deleteLecture:function(e,obj)
	{
		e.stop();
		var confirmMsg,sendMsg,successMsg, table_id = Timetable.tabs.getTableId();
		if (obj==null) 
		{
			confirmMsg='현재 예비 시간표를 초기화 하겠습니까?';
			sendMsg='table_id='+table_id;
			successMsg = '예비 시간표가 <strong>초기화</strong> 되었습니다';
		}
		else
		{
			confirmMsg='"'+obj.title+'" 예비 시간표에서 삭제 하시겠습니까?';
			sendMsg='table_id='+table_id+'&lecture_id='+obj.id;
			successMsg='<strong>'+obj.title+'</strong> 삭제 되었습니다';
		}

		if(confirm(confirmMsg))
		{
			var myRequest = new Request({
				method: 'get', 
				url: '/timetable/delete/',
				onRequest:function() {
					Notifier.setLoadingMsg('삭제하는 중입니다...');
				},
				onSuccess:function(responseText)
				{
					try{
						var resObj = JSON.decode(responseText);
						switch (resObj.result) {
						case 'OK':
							Timetable.update(resObj);
							Notifier.setMsg(successMsg);
							break;
						case 'NOT_EXIST':
							Notifier.setErrorMsg('해당 강의가 추가되어 있지 않습니다.');
							break;
						default:
							Notifier.setErrorMsg('기타 오류입니다.');
						}
					}
					catch(e)
					{
						Notifier.setErrorMsg('오류가 발생하였습니다. ('+e.message+')');
					}
				},
				onFailure:function(xhr) {
					Notifier.setErrorMsg('오류가 발생하였습니다. (요청 실패:'+xhr.status+')');
				}
			});
			myRequest.send(sendMsg);
		}
	},
	update:function(resObj)
	{
		var credit=0,au=0;
		Timetable.tabs.cleanActiveTab();
		resObj.data.each(function(obj,index)
		{
			credit+=obj.credit;
			au+=obj.au;
			var bgcolor = UDF.getColorByIndex(index);
			Timetable.buildlmodules(Timetable.tabs.getActiveTab(),obj,bgcolor,true);
		});
		
		Data.Timetables[Timetable.tabs.getTableId()] = {credit:credit,au:au};
		Timetable.tabs.updateData();
	},
	updateInfoPanel: function(obj, is_adding)
	{
		for (key in obj) {
			if ($('DS_'+key)!=null || key=='au') {
				var item = obj[key];
				if (item!=null) {
					switch (key) {
					case 'examtime':
						var time = UDF.NumericTimeToReadable(item.start) + ' ~ ' + UDF.NumericTimeToReadable(item.end);
						var name_and_time = obj.title+' '+time;
						$('DS_'+key).set('text', UDF.days[item.day]+time);
						if (is_adding)
							$('add_examtime'+item.day).set('text', name_and_time);
						break;
					case 'credit':
						if (item > 0 && is_adding)
							$('add_credit').set('text','(+'+item+')');
						$('DS_'+key).set('text',item);
						break;
					case 'au':
						if (item > 0 && is_adding)
							$('add_au').set('text','(+'+item+')');
						break;
					case 'title':
					case 'prof':
						$('DS_'+key).set('html','<p>'+item+'</p>');
						break;
					default:
						$('DS_'+key).set('text',item);
					}
				}
			}
		}
	},
	onMouseoverTemp: function(obj)
	{
		this.onMouseover(obj, true);

		this.overlap.fade('show');
		this.overlap.setStyle('display','block');
		this.overlap.empty();

		this.buildlmodules(this.overlap,obj,-1,false);
	},
	onMouseover: function(obj, is_adding)
	{
		this.updateInfoPanel(obj, is_adding);
		var tokens = obj.classroom.split(' ');
		var classroom = tokens.slice(0, tokens.length-1).join(' ');
		Map.find(classroom);
	},
	buildlmodules:function(wrap,obj,bgcolor_index,enableDelete)
	{
		var is_first = true;
		obj.times.each(function(time)
		{
			var lmodule=new Element('div',{'class':'lmodule', 'id':obj.code});
			var bg=new Element('div',{'class':'bg'});
			var textbody=new Element('div',{'class':'textbody'});
			var bgcolor, bgcolor_highlighted;
			if (bgcolor_index == -1) {
				bgcolor = '#f93';
				bgcolor_highlighted = '#f48c39';
			} else {
				bgcolor = UDF.modulecolors[bgcolor_index];
				bgcolor_highlighted = '#ffd02b';
			}
			bg.inject(lmodule);
			textbody.inject(lmodule);
			var html;
			if (enableDelete) {
				textbody.set('html','<a class="cursor"><strong>'+obj.title+'</strong></a><br />'+obj.prof+'<br />'+obj.classroom+'<br />');
				var deletelink = textbody.getElements('a');
				deletelink.addEvent('mousedown', function(ev) { ev.stopPropagation(); });
				deletelink.addEvent('click',Timetable.deleteLecture.bindWithEvent(Timetable,obj)); 
			} else
				textbody.set('html','<strong>'+obj.title+'</strong><br />'+obj.prof+'<br />'+obj.classroom+'<br />');

			var left = time.day*100+3;
			var top = Math.floor((time.start-480)/30)*21;
			var height =Math.floor((time.end-time.start)/30)*21 -2;

			bg.set({'styles':{'background':bgcolor}});

			if (enableDelete) {
				lmodule.addEvent('mouseover', Timetable.onMouseover.bind(Timetable, obj, false));

				// 같은 과목의 여러 lmodule 중 하나에만 마우스를 올려도 다함께 highlight되도록 하는 처리
				lmodule.addEvent('mouseover', function(ev) {
					$('timetable-item-'+obj.course_no+obj['class']).retrieve('mymodules').each(function(item, index) {
						item.getChildren('.bg').setStyle('background',bgcolor_highlighted);
					});
				});
				lmodule.addEvent('mouseout', function(ev) {
					$('timetable-item-'+obj.course_no+obj['class']).retrieve('mymodules').each(function(item, index) {
						item.getChildren('.bg').setStyle('background',bgcolor);
					});
				});
				// 처음 추가되는 lmodule 항목은 고유 ID를 가지며, 여기서 element storage를 이용해 자신과 다른 lmodule들의 reference를 저장한다.
				if (is_first) {
					lmodule.set('id', 'timetable-item-'+obj.course_no+obj['class']);
					is_first = false;
				}
			}

			// DOM에 lmodule 삽입
			lmodule.set({'styles':{'left':left,'top':top,'height':height}});
			lmodule.inject(wrap);

			// 고유 ID를 가진 lmodule 항목에 reference 추가
			if (enableDelete) {
				var modules = $('timetable-item-'+obj.course_no+obj['class']).retrieve('mymodules', []);
				modules.push(lmodule);
				$('timetable-item-'+obj.course_no+obj['class']).store('mymodules', modules);
			}
		}.bind(this));
	}
};
