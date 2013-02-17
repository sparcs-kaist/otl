"use strict";
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
		type:'기초필수',
		course_no:'CS202',
		class_no:'A',
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

var img_existance = function(img){
	img.error(function(){
		$(this).attr('src',Data.MediaUrl+'images/dictionary/nophoto.jpg');
	});
}
function get_star_picture(n,base) {
	var x=parseInt(n/2);
	var y=n%2;
	var z=3-x-y;
	// x : 별한개, y: 별반개, z:별0개 갯수
	var i;
	for(i=0;i<x;i++) $('<img>',{'class':'star_pictures','src':Data.MediaUrl+'images/dictionary/star.png','height':'15px'}).appendTo(base);
	for(i=0;i<y;i++) $('<img>',{'class':'star_pictures','src':Data.MediaUrl+'images/dictionary/star_half.png','height':'15px'}).appendTo(base);
	for(i=0;i<z;i++) $('<img>',{'class':'star_pictures','src':Data.MediaUrl+'images/dictionary/star_blank.png','height':'15px'}).appendTo(base);
}

var NUM_ITEMS_PER_LIST = 15;
var NUM_ITEMS_PER_DICT_COMMENT = 10;
var NUM_ITEMS_PER_INDEX_COMMENT = 5;
var NUM_ITEMS_PER_PROF_COMMENT = 6;
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
	};
Mootabs.prototype.getTableId = function()
	{
		return this.activeKey;
	};

var Utils = {
	modulecolors:
		['#FFC7FE','#FFCECE','#DFE8F3','#D1E9FF','#D2F1EE','#FFEAD1','#E1D1FF','#FAFFC1','#D4FFC1','#DEDEDE','#BDBDBD'],
	modulecolors_highlighted:
		['#feb1fd','#ffb5b5','#c9dcf2','#b7dbfd','#b5f1eb','#fbd8ae','#d4bdfd','#f1f89f','#b9f2a0','#cbc7c7','#aca6a6'],
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
	},
	NumericTimeToReadable: function(t)
	{
		var hour = Math.floor(t / 60);
		var minute = t % 60;
		return (hour < 10 ? '0':'') + hour + ':' + (minute < 10 ? '0':'') + minute;
	},
	post_to_url:function(path, params, method) 
	{
		method = method || "post";
		var form = document.createElement("form");
		form.setAttribute("method", method);
		form.setAttribute("action", path);
		for (var key in params) {
			var hiddenField = document.createElement("input");
			hiddenField.setAttribute("type", "hidden");
			hiddenField.setAttribute("name", key);
			hiddenField.setAttribute("value", params[key]);
			form.appendChild(hiddenField);
		}
		document.body.appendChild(form);
		form.submit();
	}
};

var CourseList = {
	initialize:function(tabs,contents)
	{
		this.tabs = $('#lecture_tabs');
		this.contents = $('#lecture_contents');
		this.data = Data.Lectures;
		this.dept = $('#department');
		this.classf = $('#classification');
		this.keyword = $('#keyword');
		this.apply = $('#apply');
		this.in_category = $('#in_category');

		this.loading = true;
		this.dept.selectedIndex = 0;
		this.registerHandles();
		this.getAutocompleteList();
		if (this.pre_active_tab === -1) this.onChange();
		else this.onPreChange();
	},
	registerHandles:function()
	{
		$(this.dept).bind('change', $.proxy(this.onClassChange, this));
		$(this.classf).bind('change', $.proxy(this.onClassChange, this));
		$(this.apply).bind('click', $.proxy(this.onChange, this));
		$(this.in_category).bind('change', $.proxy(this.onInCategoryChange, this));
		$(this.keyword).bind('keypress', $.proxy(function(e) { if(e.keyCode == 13) { this.onChange(); }}, this));
	},
	getAutocompleteList:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		var in_category = $(this.in_category).is(':checked');
		var conditions = {};
		if( in_category )
			conditions = {'year': Data.ViewYear, 'term': Data.ViewTerm, 'dept': dept, 'type': classification, 'lang': USER_LANGUAGE};
		else
			conditions = {'year': Data.ViewYear, 'term': Data.ViewTerm, 'dept': -1, 'type': '전체보기', 'lang': USER_LANGUAGE};
		$.ajax({
			type: 'GET',
			url: '/dictionary/autocomplete/',
			data: conditions,
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
	onInCategoryChange:function()
	{
		this.getAutocompleteList();
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		if( keyword != '' )
			this.onChange();
	},
	onClassChange:function()
	{
		var in_category = $(this.in_category).is(':checked');
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		if( in_category )
			this.getAutocompleteList();
		if( in_category || keyword == '')
			this.onChange();
	},
	onChange:function()
	{
		var dept = $(this.dept).val();
		var classification = $(this.classf).val();
		var keyword = $(this.keyword).val().replace(/^\s+|\s+$/g, '');
		var in_category = $(this.in_category).is(':checked');
		//TODO: classification을 언어와 상관 없도록 고쳐야 함
		if (dept == '-1' && USER_LANGUAGE == 'ko' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('키워드 없이 학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else if (dept == '-1' && USER_LANGUAGE == 'en' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('You must select a course type if you want to see \'ALL\' departments without keywords.');
		else {
			if( in_category || keyword == '')
				this.filter({'dept':dept,'type':classification,'lang':USER_LANGUAGE,'keyword':keyword});
			else
				this.filter({'dept':-1,'type':'전체보기','lang':USER_LANGUAGE,'keyword':keyword});
		}
	},
	onPreChange:function()
	{
		if (this.pre_keyword === false) this.pre_keyword = '';

		document.getElementById("department").selectedIndex = this.pre_dept;
		document.getElementById("classification").selectedIndex = this.pre_classification;
		document.getElementById("keyword").value = this.pre_keyword;
		document.getElementById("in_category").checked = this.pre_in_category;

		var dept = document.getElementById("department")[this.pre_dept].value;
		var classification = document.getElementById("classification")[this.pre_classification].value;
		var keyword = this.pre_keyword.replace(/^s+|\s+$/g, '');
		var in_category = this.pre_in_category;
		var active_tab = this.pre_active_tab-1;

		if (dept == '-1' && USER_LANGUAGE == 'ko' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('키워드 없이 학과 전체보기는 과목 구분을 선택한 상태에서만 가능합니다.');
		else if (dept == '-1' && USER_LANGUAGE == 'en' && classification == '전체보기' && keyword == '')
			Notifier.setErrorMsg('You must select a course type if you want to see \'ALL\' departments without keywords.');
		else {
			if( in_category || keyword == '')
				this.filter({'dept':dept,'type':classification,'lang':USER_LANGUAGE,'keyword':keyword},active_tab);
			else
				this.filter({'dept':-1,'type':'전체보기','lang':USER_LANGUAGE,'keyword':keyword},active_tab);
		}
		this.pre_active_tab=-1;
	},
	clearList:function()
	{
		CourseList.contents.empty(); 
		CourseList.buildTabs(CourseList.contents.children().length);
	},
	addToListMultiple:function(obj,active_tab)
	{
		if (active_tab===undefined) active_tab=0;
		CourseList.contents.empty(); 
		var max = NUM_ITEMS_PER_LIST;
		var count=0;
                var flag=0;
		var content = $('<div>', {'class': 'lecture_content'});
		content.appendTo(CourseList.contents);
		var currCategory='교수정보';
                
		$.each(obj.professors, function(index, item) {
                        if(flag==0&&count==0) {
                            $('<h4>').text(currCategory).appendTo(content);
                            flag=1;
                        }
                        if(count>=max) {
				content = $('<div>', {'class':'lecture_content'}).appendTo(CourseList.contents);
				$('<h4>').text(currCategory).appendTo(content);
				count=0;
                        } else
                                count++;

			var el = $('<a>').text(item.professor_name).appendTo(content);
			Utils.clickable(el);

			el.bind('mousedown', $.proxyWithArgs(CourseList.seeProfessorInfo, CourseList, item));
                });
		$.each(obj.courses, function(index, item) {
			var key = item.type;
			if (currCategory != key) {
				currCategory = key;
				if (count < max) $('<h4>').text(currCategory).appendTo(content);
			}

			if (count>=max) {
				content = $('<div>', {'class':'lecture_content'}).appendTo(CourseList.contents);
				$('<h4>').text(currCategory).appendTo(content);
				count=0;
			} else
				count++;
			var temp_1 = item.title.split("<");
			var temp_2 = temp_1[0].split("[");
			var el = $('<a>').text(temp_2[0]).appendTo(content);
			Utils.clickable(el);

			el.bind('mousedown', $.proxyWithArgs(CourseList.seeCourseComments, CourseList, item));
		});
		CourseList.buildTabs(CourseList.contents.children().length);
		this.mootabs = new Mootabs($('#lecture_tabs'), $('#lecture_contents'));
		this.mootabs.activate(active_tab);
	},
	filter:function(conditions,active_tab)
	{
		//TODO: conditions.type와 상관 없도록 고쳐야 함
		if (conditions.type == undefined){
			conditions.type = '전체보기';
		}
		$.ajax({
			type: 'GET',
			url: '/dictionary/search/',
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
					if (resObj.courses.length == 0 && resObj.professors.length == 0) {
						CourseList.clearList();
						if (!this.loading)
							Notifier.setErrorMsg(gettext('과목 정보를 찾지 못했습니다.'));
					} else {
						CourseList.addToListMultiple(resObj,active_tab);
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
	seeCourseComments:function(e,obj)
	{
		var old_code = obj.old_code;
		var url = '/dictionary/view/' + old_code + '/';

		var dept = document.getElementById("department").selectedIndex;
		var classification = document.getElementById("classification").selectedIndex;
		var keyword = $(this.keyword).val();
		var in_category = $(this.in_category).is(':checked');
		var active_tab = $('div[class="lecture_tab active"]').text();
		var sendData = {'dept':dept, 'classification':classification, 'keyword':keyword, 'in_category':in_category, 'active_tab':active_tab};

		Utils.post_to_url(url, sendData, 'GET');
	},
	seeProfessorInfo:function(e,obj)
	{
		var professor_id = obj.professor_id;
		var url = '/dictionary/professor/' + professor_id + '/';

		var dept = document.getElementById("department").selectedIndex;
		var classification = document.getElementById("classification").selectedIndex;
		var keyword = $(this.keyword).val();
		var in_category = $(this.in_category).is(':checked');
		var active_tab = $('div[class="lecture_tab active"]').text();
		var sendData = {'dept':dept, 'classification':classification, 'keyword':keyword, 'in_category':in_category, 'active_tab':active_tab};

		Utils.post_to_url(url, sendData, 'GET');
	},
};

var DictionaryCommentList = {
	initialize:function()
	{
		this.summary = $('#course-summary');
		this.lecture_summary = $('#lecture-summary');
		this.comments = $('#course-comment-view');
		this.lecture_rating = $('#lecture-rating');
		this.onLoad();
		this.registerHandles();
                this.loading=true;
				this.last_index=-1;
	},
	onLoad:function()
	{
		this.addToMultipleProfessor(Data.Professors);
		this.onChangeProfessor(DictionaryCommentList, null);

	},
	registerHandles:function()
	{
		$('#course-comment-add-submit').bind('mousedown', $.proxy(this.addComment, this));
		$('#new-comment-semester').change(function(){
			if(Data.current_professor_id == -1){
				DictionaryCommentList.addToProfessor();
			}
		});
                $(window).scroll(function() {
                    if(!DictionaryCommentList.loading){
                    if($(window).scrollTop() + $(window).height() == $(document).height()) {
			    DictionaryCommentList.showMoreComments();

                    }
                    }
                });

	},

	showMoreComments:function()
	{
		if (Data.comment_id!=0){
			var conditions = {'course_id': Data.Course.id, 'next_comment_id': Data.comment_id, 'professor_id': Data.current_professor_id};
			$.ajax({
				type: 'GET',
				url: '/dictionary/show_more_comments/',
				data: conditions,
				dataType: 'json',
				success: $.proxy(function(resObj) {
					try {
						Data.comment_id = resObj.next_comment_id;
						DictionaryCommentList.addToMultipleComment(resObj.comments);
                                                Data.DictionaryComment = Data.DictionaryComment.concat(resObj.comments);
					} catch(e) {
						Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
					}
                                        this.loading = false;

				}, this),
				error: $.proxy(function(xhr) {
					if (suppress_ajax_errors)
						return;
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
                                        this.loading = false;
				}, this)
			});
		}

	},
	showSummary:function()
	{
		if(Data.user_id==null)
			Notifier.setErrorMsg(gettext('과목 정보를 수정하기 위해서는 로그인해야 합니다.'));
		else{
			$('#course-explain').hide();
			$('#course-require').hide();
			$('#course-summary-add-img').hide();
			$('#course-explain-add').show();
			$('#course-require-add').show();
			$('#course-summary-complete-img').show();
		}
	},
	showLectureSummary:function()
	{
		if(Data.user_id==null)
			Notifier.setErrorMsg(gettext('강의 정보를 수정하기 위해서는 로그인해야 합니다.'));
		else{
			$('#lecture-homepage-html').hide();
			$('#lecture-mainbook-html').hide();
			$('#lecture-subbook-html').hide();
			$('#lecture-summary-add-img').hide();
			$('#lecture-homepage-add').show();
			$('#lecture-mainbook-add').show();
			$('#lecture-subbook-add').show();
			$('#lecture-summary-complete-img').show();
		}
	},
	addSummary:function()
	{
		var new_explain_content = $("#course-explain-add").val();
		var new_require_content = $('#course-require-add').val();
		var course_id = Data.Course.id;
                var writer_id = Data.user_id;
                $.ajax({
                    type: 'POST',
                    url: '/dictionary/add_summary/',
  					data: {'content': new_explain_content, 'require': new_require_content, 'course_id': course_id, 'writer_id': writer_id},
                    dataType: 'json',
                    success: $.proxy(function(resObj) {
                        try {
                            if (resObj.result=='OK') {
				$($("#course-change-user")).text(gettext("마지막 고침 : ")+resObj.summary.written_datetime + " " + resObj.summary.writer + " ");
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
		var output_explain = new_explain_content
		var output_require = new_require_content;
		$("#course-require").text(output_require);
		$("#course-explain").text(output_explain);
		$('#course-explain-add').hide();
		$('#course-require-add').hide();
		$('#course-summary-complete-img').hide();
		$('#course-explain').show();
		$('#course-require').show();
		$('#course-summary-add-img').show();
	},
	addLectureSummary:function()
	{
		var new_homepage_content = $("#lecture-homepage-add").val();
		var new_mainbook_content = $('#lecture-mainbook-add').val();
		var new_subbook_content = $('#lecture-subbook-add').val();
		var course_id = Data.Course.id;
		var prof_id = Data.current_professor_id;
                var writer_id = Data.user_id;
                $.ajax({
                    type: 'POST',
                    url: '/dictionary/add_lecture_summary/',
  					data: {'homepage': new_homepage_content, 'mainbook': new_mainbook_content, 'subbook': new_subbook_content, 'course_id': course_id, 'writer_id': writer_id, 'professor_id':prof_id},
                    dataType: 'json',
                    success: $.proxy(function(resObj) {
                        try {
                            if (resObj.result=='OK') {
				 $($("#lecture-change-user")).text(gettext("마지막 고침 : ")+resObj.summary.written_datetime + " " + resObj.summary.writer + " ");

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
		var output_homepage = new_homepage_content
		var output_mainbook = new_mainbook_content
		var output_subbook = new_subbook_content

		$('#lecture-homepage-html').text(output_homepage);
		$('#lecture-mainbook-html').text(output_mainbook);
		$('#lecture-subbook-html').text(output_subbook);
		$('#lecture-homepage-add').hide();
		$('#lecture-mainbook-add').hide();
		$('#lecture-subbook-add').hide();
		$('#lecture-summary-complete-img').hide();
		$('#lecture-homepage-html').show();
		$('#lecture-mainbook-html').show();
		$('#lecture-subbook-html').show();
		$('#lecture-summary-add-img').show();
	},


	addComment:function()
	{
		var new_comment_content = $('#course-comment-add-text').val();
		var new_comment_load = $('#new-comment-load').val();
		var new_comment_score = $('#new-comment-score').val();
		var new_comment_gain = $('#new-comment-gain').val();
		var new_comment_year = parseInt($('#new-comment-semester').val()/10);
		var new_comment_semester = $('#new-comment-semester').val()%10;
		var new_comment_professor = Data.current_professor_id;
		if(new_comment_professor == -1)
			new_comment_professor = $('#new-comment-professor').val();
		if (new_comment_load==-1 || new_comment_score==-1 || new_comment_gain==-1) {
			Notifier.setErrorMsg(gettext('로드, 학점, 남는거를 선택하세요.'));
		}
		else if(new_comment_semester==0 || new_comment_professor==0){
			Notifier.setErrorMsg(gettext('학기, 담당교수를 선택하세요.'));
		}
		else {
			$.ajax({
				type: 'POST', 
				url: '/dictionary/add_comment/',
				data: {'comment': new_comment_content, 'load': new_comment_load, 'score': new_comment_score, 'gain': new_comment_gain, 'course_id': Data.Course.id, 'professor_id': new_comment_professor, 'year': new_comment_year, 'semester': new_comment_semester, 'status': Data.current_professor_id},
				dataType: 'json',
				success: $.proxy(function(resObj) {
					try {
						if (resObj.result=='ADD') {
							DictionaryCommentList.addToFront(resObj.comment);
							DictionaryCommentList.addNewComment(resObj.comment);
							$('#course-comment-add-text').val("");
							$('#new-comment-load').val(0);
							$('#new-comment-score').val(0);
							$('#new-comment-gain').val(0);
							$('#new-comment-semester').val(0);
							$('#new-comment-professor').val(0);
							if(Data.current_professor_id == -1)
							{
								$($("#course-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
								$($("#course-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
								$($("#course-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
								$("#course-eval-average").text(((resObj.average['avg_score']+resObj.average['avg_load']+resObj.average['avg_gain'])/3).toFixed(1));
								$("#course-eval-count").text(gettext("평가자 수 : ") + resObj.comment_num + gettext("명"));
							}
							else
							{
								$($("#lecture-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
								$($("#lecture-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
								$($("#lecture-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
								$("#lecture-eval-average").text(((resObj.average['avg_score']+resObj.average['avg_load']+resObj.average['avg_gain'])/3).toFixed(1));
								$("#lecture-eval-count").text(gettext("평가자 수 : ") + resObj.comment_num + gettext("명"));
							}
						} else if (resObj.result='ALREADY_WRITTEN') {
							Notifier.setErrorMsg(gettext('이미 등록하셨습니다.'));
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
		}
	},
	deleteComment:function(e,obj, comment) 
	{
		$.ajax({
			type: 'POST',
			url: '/dictionary/delete_comment/',
			data: {'comment_id': obj.comment_id, 'prof_id':Data.current_professor_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='DELETE') {
						comment.remove();
						if(Data.current_professor_id == -1)
						{
							$($("#course-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
							$($("#course-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
							$($("#course-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
							$("#course-eval-average").text(((resObj.average['avg_score']+resObj.average['avg_load']+resObj.average['avg_gain'])/3).toFixed(1));
							$("#course-eval-count").text(gettext("평가자 수 : ") + resObj.comment_num + gettext("명"));
						}
						else
						{
							$($("#lecture-eval").children()[0]).text("학점 : "+resObj.average['avg_score'].toFixed(1));
							$($("#lecture-eval").children()[1]).text("로드 : "+resObj.average['avg_load'].toFixed(1));
							$($("#lecture-eval").children()[2]).text("남는거 : "+resObj.average['avg_gain'].toFixed(1));
							$("#lecture-eval-average").text(((resObj.average['avg_score']+resObj.average['avg_load']+resObj.average['avg_gain'])/3).toFixed(1));
							$("#lecture-eval-count").text(gettext("평가자 수 : ") + resObj.comment_num + gettext("명"));
						}
					} else if (resObj=='REMOVE_NOT_EXIST') {
						Notifier.setErrorMsg(gettext('잘못된 접근입니다.'));
					}
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if (xhr.status == 403) {
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},
	addToMultipleComment:function(obj)
	{
		var total = $(obj).length;
		$.each(obj, function(index, item) {
			var enableDelete = (item.writer_id == Data.user_id);
			var comment = $('<div>', {'class': 'dictionary_comment'});
			var comment_output = item.comment
			comment.appendTo(DictionaryCommentList.comments);

			var left_div_comment = $('<div>', {'class': 'dictionary_comment_left'});
			var right_div_comment = $('<div>', {'class': 'dictionary_comment_right'});
			if(Data.current_professor_id==-1)
				left_div_comment.appendTo(comment);
			else
				right_div_comment.css("width","750px");
			right_div_comment.appendTo(comment);
			var prof_img = $('<img>', {'class': 'dictionary_comment_prof_photo', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+item.professor[0].professor_id+'.jpg'});
			img_existance(prof_img);
			prof_img.appendTo(left_div_comment);

			var right_top_div = $('<div>', {'class': 'dictionary_comment_right_top'});
			var right_top_div_eval = $('<div>',{'class':'dictionary_comment_right_top_eval'});

			right_top_div.appendTo(right_div_comment);
			$('<div>', {'class': 'dictionary_comment_semester'}).text('<' + item.year + ' ' + gettext(item.semester==1?"봄":"가을") + '>').appendTo(right_top_div);
			if(Data.current_professor_id==-1){
				$('<div>', {'class': 'dictionary_comment_prof'}).text(gettext("담당교수 : ")).appendTo(right_top_div);
				for(var i=0;i<item.professor.length;i++)
				{
					$('<div>', {'class': 'dictionary_comment_prof_name'}).text(item.professor[i].professor_name + ((i!=item.professor.length-1)?gettext(","):gettext(""))).appendTo(right_top_div);
				}
			}
			else
				$('<div>', {'class': 'dictionary_comment_lecture'}).text(item.lecture_title).appendTo(right_top_div);
			right_top_div_eval.appendTo(right_top_div);

			var comment_eval = $('<div>', {'class': 'dictionary_comment_eval'});
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("학점 :")).appendTo(comment_eval);
			get_star_picture(item.score,comment_eval);
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("로드 :")).appendTo(comment_eval);
			get_star_picture(item.load,comment_eval);
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("남는거 :")).appendTo(comment_eval);
			get_star_picture(item.gain,comment_eval);
			comment_eval.appendTo(right_top_div_eval);


			var right_mid_div = $('<div>', {'class': 'dictionary_comment_right_mid'});
			right_mid_div.appendTo(right_div_comment);
			$('<pre>', {'class': 'dictionary_comment_content'}).text(comment_output).appendTo(right_mid_div);

			var right_bot_div = $('<div>',{'class':'dictionary_comment_right_bot'});
			right_bot_div.appendTo(right_div_comment);
			if (enableDelete) {	
				var deletelink = $('<img>', {'class': 'dictionary_comment_delete','src':Data.MediaUrl+'images/dictionary/x_sign.jpg'});
				deletelink.appendTo(right_bot_div);
				deletelink.bind('click', $.proxyWithArgs(DictionaryCommentList.deleteComment, DictionaryCommentList, item, comment));
			}
			$('<div>',{'class':'dictionary_comment_date'}).text(item.written_date).appendTo(right_bot_div);
			$('<div>',{'class':'dictionary_comment_writer'}).text(gettext("작성자") + " : " + item.writer_nickname).appendTo(right_bot_div);


   			if (index != total-1){
   				$('<hr>',{'class': 'dictionary_comment_line'}).appendTo(comment);
   			}
		});
	},
	addToMultipleProfessor:function(obj)
	{
		var professor_tabs = $('#course-professor');
		var default_tab = $('<div>', {'class': 'course-professor-tab'}).text('일반');

		default_tab.appendTo(professor_tabs);
		default_tab.bind('click', $.proxyWithArgs(DictionaryCommentList.onChangeProfessor, DictionaryCommentList, null));

		$.each(obj, function(index, item) {
			var professor_tab = $('<div>', {'class': 'course-professor-tab'}).text(item.professor_name);
			professor_tab.appendTo(professor_tabs);
			item.index=index;

			professor_tab.bind('click', $.proxyWithArgs(DictionaryCommentList.onChangeProfessor, DictionaryCommentList, item));
		});
	},
	clearComment:function()
	{
		this.comments.empty();
		Data.DictionaryComment = [];
	},
	clearEval: function()
	{
		this.eval.empty();
	},
	clearSummary:function()
	{
		this.summary.empty();
	},
	clearLectureSummary:function()
	{
		this.lecture_summary.empty();
	},
	clearLectureRating:function()
	{
		this.lecture_rating.empty();
		this.lecture_rating.hide();
	},
	clearBox:function()
	{
		$('#new-comment-semester').empty();
		$('#new-comment-professor').empty();
		$('#new-comment-score').val("");
		$('#new-comment-load').val("");
		$('#new-comment-gain').val("");
		$('#course-comment-add-text').val("");
	},
	clearProfessorBox:function()
	{
		$('#new-comment-professor').empty();
	},
	update:function(obj)
	{
		Data.DictionaryComment = obj;
	},
	addToFront:function(obj)
	{
		Data.DictionaryComment = obj.concat(Data.DictionaryComment);
	},
	addToGeneralSummary:function(obj)
	{
		var left_div = $('<div>', {'id': 'course-intro'});
		var general_summary = obj.summary;
		if (general_summary==null){
			var output_explain = "";
			var output_require = "";
		}
		else{
			var output_explain = general_summary.summary;
			var output_require = general_summary.prerequisite;
		}
		var temp_1 = Data.Course.title.split("<");
		var temp_2 = temp_1[0].split("[");
		$('<div>', {'id': 'course-subject'}).text(temp_2[0]).appendTo(left_div);
		$('<hr>',{'id': 'course-line'}).appendTo(left_div);
		$('<div>', {'id': 'course-explain-title'}).text(gettext("과목 설명")).appendTo(left_div);
		$('<pre>', {'id': 'course-explain'}).text(output_explain).appendTo(left_div);
		$('<textarea>', {'id': 'course-explain-add'}).text(output_explain).appendTo(left_div);
		$('<div>', {'id': 'course-require-title'}).text(gettext("선수 과목")).appendTo(left_div);
		$('<pre>', {'id': 'course-require'}).text(output_require).appendTo(left_div);
		$('<textarea>', {'id': 'course-require-add'}).text(output_require).appendTo(left_div);

		var right_div = $('<div>', {'id': 'course-score'});
		$('<div>', {'id': 'course-eval-title'}).text("TOTAL SCORE").appendTo(right_div);

		var right_div_eval = $('<div>', {'id': 'course-eval'});
		$('<div>', {'class': 'course-eval-score'}).text(gettext("학 점 ") + obj.average['avg_score'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'course-eval-score'}).text(gettext("로 드 ") + obj.average['avg_load'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'course-eval-score'}).text(gettext("남는거 ") + obj.average['avg_gain'].toFixed(1)).appendTo(right_div_eval);
		right_div_eval.appendTo(right_div);

		$('<div>', {'id': 'course-eval-average'}).text(((obj.average['avg_score']+obj.average['avg_load']+obj.average['avg_gain'])/3).toFixed(1)).appendTo(right_div);
		$('<div>', {'id': 'course-eval-count'}).text(gettext("평가자 수 : ") +obj.comment_num + gettext("명")).appendTo(right_div);

		var bottom_div = $('<div>', {'id': 'course-summary-bottom'});
		var bottom_img = $('<div>', {'id': 'course-bottom-img'});
		var add_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'course-summary-add-img'});
		var complete_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'course-summary-complete-img'});
		if(general_summary==null)
			var bottom_text = $('<div>', {'id': 'course-change-user'}).text("");
		else
			var bottom_text = $('<div>', {'id': 'course-change-user'}).text(gettext("마지막 고침 : ") + general_summary.written_datetime + " " + general_summary.writer + " ");

		bottom_text.appendTo(bottom_div);
		add_img.appendTo(bottom_img);
		complete_img.appendTo(bottom_img);
		bottom_img.appendTo(bottom_div);
		add_img.bind('click', $.proxy(this.showSummary, this));
		complete_img.bind('click', $.proxy(this.addSummary, this));
		bottom_div.appendTo(left_div);

		left_div.appendTo(this.summary);
		right_div.appendTo(this.summary);

		$('#course-explain-add').hide();
		$('#course-require-add').hide();
		$('#course-summary-complete-img').hide();
	},
	addToLectureSummary:function(obj)
	{
		var left_div = $('<div>', {'id': 'lecture-intro'});
		if(obj.summary==null){
			var output_homepage = "";
			var output_mainbook = "";
			var output_subbook = "";
		}
		else{
			var output_homepage = obj.summary.homepage;
			var output_mainbook = obj.summary.main_material;
			var output_subbook = obj.summary.sub_material;
		}
		$('<div>', {'id': 'lecture-subject'}).text(obj.lecture_title).appendTo(left_div);
		$('<hr>', {'id': 'lecture-line'}).appendTo(left_div);
		
		var left_left_div = $('<div>', {'id': 'lecture-prof-photo'});
		var prof_img = $('<img>', {'id': 'lecture-prof-img', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+Data.current_professor_id+'.jpg'});
		img_existance(prof_img);
		prof_img.appendTo(left_left_div);

		left_left_div.appendTo(left_div);
		$('<div>', {'id': 'lecture-prof-name'}).text(gettext("prof. ")+obj.prof_name).appendTo(left_left_div);

		var lec_homepage = $('<div>', {'id': 'lecture-homepage'});
		$('<div>', {'id': 'lecture-homepage-title'}).text(gettext("과목 홈페이지")).appendTo(lec_homepage);
		$('<pre>', {'id': 'lecture-homepage-html'}).text(output_homepage).appendTo(lec_homepage);
		$('<textarea>', {'id': 'lecture-homepage-add'}).text(output_homepage).appendTo(lec_homepage);	
		lec_homepage.appendTo(left_div);
		
		var lec_mainbook = $('<div>', {'id': 'lecture-mainbook'});
		$('<div>', {'id': 'lecture-mainbook-title'}).text(gettext("주교재")).appendTo(lec_mainbook);
		$('<pre>', {'id': 'lecture-mainbook-html'}).text(output_mainbook).appendTo(lec_mainbook);
		$('<textarea>', {'id': 'lecture-mainbook-add'}).text(output_mainbook).appendTo(lec_mainbook);
		lec_mainbook.appendTo(left_div);

		var lec_subbook = $('<div>', {'id': 'lecture-subbook'});
		$('<div>', {'id': 'lecture-subbook-title'}).text(gettext("부교재")).appendTo(lec_subbook);
		$('<pre>', {'id': 'lecture-subbook-html'}).text(output_subbook).appendTo(lec_subbook);
		$('<textarea>', {'id': 'lecture-subbook-add'}).text(output_subbook).appendTo(lec_subbook);
		lec_subbook.appendTo(left_div);

		var right_div = $('<div>', {'id': 'lecture-score'});
		var right_div_eval = $('<div>', {'id': 'lecture-eval'});
		$('<div>', {'id': 'lecture-eval-title'}).text("TOTAL SCORE").appendTo(right_div);
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("학 점 ") + obj.average['avg_score'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("로 드 ") + obj.average['avg_load'].toFixed(1)).appendTo(right_div_eval);
		$('<div>', {'class': 'lecture-eval-score'}).text(gettext("남는거 ") + obj.average['avg_gain'].toFixed(1)).appendTo(right_div_eval);

		right_div_eval.appendTo(right_div);
		
		$('<div>', {'id': 'lecture-eval-average'}).text(((obj.average['avg_score']+obj.average['avg_load']+obj.average['avg_gain'])/3).toFixed(1)).appendTo(right_div);
		$('<div>', {'id': 'lecture-eval-count'}).text(gettext("평가자 수 : ") +obj.comment_num + gettext("명")).appendTo(right_div);

		var right_right_div = $('<div>', {'id': 'lecture-lec-score'});
		var right_div_lec_eval = $('<div>', {'id': 'lecture-lec-eval'});
		$('<div>', {'id': 'lecture-lec-eval-title'}).text(gettext("강의평가결과")).appendTo(right_right_div);

		$('<div>', {'class': 'lecture-lec-eval-score'}).text(gettext("응답률 ")+obj.rating.rate+gettext(" (")+obj.rating.num_effective+gettext("/")+obj.rating.num_students+gettext(")")).appendTo(right_div_lec_eval);
		$('<div>', {'class': 'lecture-lec-eval-score'}).text(gettext("표준편차 ")+obj.rating.deviation).appendTo(right_div_lec_eval);

		right_div_lec_eval.appendTo(right_right_div);

		var lecture_rating_href = $('<a>', {'id': 'lecture-lec-eval-rating'}).text(obj.rating.score);
		lecture_rating_href.appendTo(right_right_div);
		lecture_rating_href.bind('click',function() {
			$('#lecture-rating').show();});

		var bottom_div = $('<div>', {'id': 'lecture-summary-bottom'});
		var bottom_img = $('<div>', {'id': 'lecture-bottom-img'});
		var add_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'lecture-summary-add-img'});
		var complete_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'lecture-summary-complete-img'});
		if(obj.summary==null)
			var bottom_text = $('<div>', {'id': 'lecture-change-user'}).text("");
		else
			var bottom_text = $('<div>', {'id': 'lecture-change-user'}).text(gettext("마지막 고침 : ") + obj.summary.written_datetime + " " + obj.summary.writer + " ");

		bottom_text.appendTo(bottom_div);
		add_img.appendTo(bottom_img);
		complete_img.appendTo(bottom_img);
		bottom_img.appendTo(bottom_div);
		add_img.bind('click', $.proxy(this.showLectureSummary, this));
		complete_img.bind('click', $.proxy(this.addLectureSummary, this));

		bottom_div.appendTo(left_div);
		left_div.appendTo(this.summary);
		right_div.appendTo(this.summary);
		right_right_div.appendTo(this.summary);

		$('#lecture-homepage-add').hide();
		$('#lecture-mainbook-add').hide();
		$('#lecture-subbook-add').hide();
		$('#lecture-summary-complete-img').hide();

	},
	addToLectureRating:function(obj){
		var close = $('<div>', {'id':'lecture-rating-close'});
		$('<img>', {'src':Data.MediaUrl+'images/dictionary/x_sign.jpg'}).appendTo(close);
		close.appendTo(this.lecture_rating);
		close.bind('click',function() {
			$('#lecture-rating').hide();});

		var table = $('<table>', {'id':'lecture-rating-table'});
		var first_row = $('<tr>', {'id':'lecture-rating-table-firstrow'});
		$('<td>').text(gettext("연도")).appendTo(first_row);
		$('<td>').text(gettext("학기")).appendTo(first_row);
		$('<td>').text(gettext("분반")).appendTo(first_row);
		$('<td>').text(gettext("체계적 구성")).appendTo(first_row);
		$('<td>').text(gettext("강의의 이해도")).appendTo(first_row);
		$('<td>').text(gettext("창의적 사고 장려")).appendTo(first_row);
		$('<td>').text(gettext("강의의 도움정도")).appendTo(first_row);
		$('<td>').text(gettext("평균")).appendTo(first_row);
		first_row.appendTo(table);
	    $.each(obj, function(index, item) {
			var row = $('<tr>', {'class':'lecture-rating-table-row'});
			$('<td>').text(item.year).appendTo(row);
			$('<td>').text(gettext(item.semester==1?"봄":"가을")).appendTo(row);
			$('<td>').text(item.class_no).appendTo(row);
			$('<td>').text(item.composition).appendTo(row);
			$('<td>').text(item.understand).appendTo(row);
			$('<td>').text(item.creative).appendTo(row);
			$('<td>').text(item.support).appendTo(row);
			$('<td>').text(item.average).appendTo(row);
			row.appendTo(table);
		});
		table.appendTo(this.lecture_rating);
	},
	addToProfessor:function(){
		this.clearProfessorBox();
		var new_comment_year = parseInt($('#new-comment-semester').val()/10);
		var new_comment_semester = $('#new-comment-semester').val()%10;
		$.ajax({
			type: 'POST',
			url: '/dictionary/get_year_list/',
			data: {'course_id': Data.Course.id, 'year':new_comment_year, 'semester':new_comment_semester},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					var professor_box = $('#new-comment-professor');
					$.each(resObj.professor, function(index, item){
						professor_box.prepend('<option value=' + item.professor_id + '>' + item.professor_name + '</option>');
					});
					professor_box.prepend('<option value=0></option>');
				} catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if (xhr.status == 403) {
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},
	addToSemester:function(obj){
		var semester_box = $('#new-comment-semester');
	    $.each(obj, function(index, item) {
			semester_box.prepend('<option value=' + (item.year*10+item.semester) + '>' + item.year + " " + gettext(item.semester==1?"봄":"가을") + '</option>');
		});
		semester_box.prepend('<option value=0></option>');
	},
	onChangeProfessor:function(e,obj)
	{
		this.clearComment();
		this.clearSummary();
		this.clearBox();
		this.clearLectureSummary();
		this.clearLectureRating();
		Data.comment_id = -1;		
		$($('.course-professor-tab')[this.last_index+1]).css({"color":"#555555","border-color":"#EEEEEE","background-color":"#FFFFFF"});
		if(obj==null) {
			this.last_index=-1;
			Data.current_professor_id = -1;
			$('#course-comment-add-professor').show();
			$('#course-comment-add-semester').css("margin-right","0px");
		}
		else {
			this.last_index=obj.index;
			Data.current_professor_id = obj.professor_id;
			$('#course-comment-add-professor').hide();
			$('#course-comment-add-semester').css("margin-right","272px");
		}
		$($('.course-professor-tab')[this.last_index+1]).css({"color":"#FFFFFF","border-color":"#C3D9FF","background-color":"#C3D9FF"});
		$.ajax({
			type: 'POST',
			url: '/dictionary/get_summary_and_semester/',
			data: {'professor_id': Data.current_professor_id,  'course_id' : Data.Course.id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if(resObj.result=="GENERAL"){
					    this.addToGeneralSummary(resObj);
					}
					else if(resObj.result=="GEN_EMPTY")
					{
					    resObj.summary=null;	
				            this.addToGeneralSummary(resObj);
					}
					else if(resObj.result=="PROF")
					{
					    this.addToLectureSummary(resObj);
						this.addToLectureRating(resObj.rating_all);
					}
					else if(resObj.result=="PROF_EMPTY")
					{
					    resObj.summary=null;
					    this.addToLectureSummary(resObj);
						this.addToLectureRating(resObj.rating_all);
					}
					this.showMoreComments();
					this.addToSemester(resObj.semester);
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}	
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if(xhr.status == 403){
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else{
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	},
    addNewComment:function(obj){
	    $.each(obj, function(index, item) {
			var enableDelete = (item.writer_id == Data.user_id);
			var comment = $('<div>', {'class': 'dictionary_comment'});
			var comment_output = item.comment
			comment.prependTo(DictionaryCommentList.comments);

			var left_div_comment = $('<div>', {'class': 'dictionary_comment_left'});
			var right_div_comment = $('<div>', {'class': 'dictionary_comment_right'});
			if(Data.current_professor_id==-1)
				left_div_comment.appendTo(comment);
			else
				right_div_comment.css("width","750px");
			right_div_comment.appendTo(comment);
			var prof_img=$('<img>', {'class': 'dictionary_comment_prof_photo', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+item.professor[0].professor_id+'.jpg'});
			img_existance(prof_img);
			prof_img.appendTo(left_div_comment);

			var right_top_div = $('<div>', {'class': 'dictionary_comment_right_top'});
			var right_top_div_eval = $('<div>',{'class':'dictionary_comment_right_top_eval'});

			right_top_div.appendTo(right_div_comment);
			$('<div>', {'class': 'dictionary_comment_semester'}).text('<' + item.year + ' ' + gettext(item.semester==1?"봄":"가을")+ '>').appendTo(right_top_div);
			if(Data.current_professor_id==-1){
				$('<div>', {'class': 'dictionary_comment_prof'}).text(gettext("담당교수 : ")).appendTo(right_top_div);
				for(var i=0;i<item.professor.length;i++)
				{
					$('<div>', {'class': 'dictionary_comment_prof_name'}).text(item.professor[i].professor_name + ((i!=item.professor.length-1)?gettext(","):gettext(""))).appendTo(right_top_div);
				}
			}
			else
				$('<div>', {'class': 'dictionary_comment_lecture'}).text(item.lecture_title).appendTo(right_top_div);
			right_top_div_eval.appendTo(right_top_div);

			var comment_eval = $('<div>', {'class': 'dictionary_comment_eval'});
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("학점 :")).appendTo(comment_eval);
			get_star_picture(item.score,comment_eval);
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("로드 :")).appendTo(comment_eval);
			get_star_picture(item.load,comment_eval);
			$('<div>',{'class':'dictionary_comment_names'}).text(gettext("남는거 :")).appendTo(comment_eval);
			get_star_picture(item.gain,comment_eval);
			comment_eval.appendTo(right_top_div_eval);

			var right_mid_div = $('<div>', {'class': 'dictionary_comment_right_mid'});
			right_mid_div.appendTo(right_div_comment);
			$('<pre>', {'class': 'dictionary_comment_content'}).text(comment_output).appendTo(right_mid_div);

			var right_bot_div = $('<div>',{'class':'dictionary_comment_right_bot'});
			right_bot_div.appendTo(right_div_comment);
			if (enableDelete) {
				var deletelink = $('<img>', {'class': 'dictionary_comment_delete','src':Data.MediaUrl+'images/dictionary/x_sign.jpg'});
				deletelink.appendTo(right_bot_div);
				deletelink.bind('click', $.proxyWithArgs(DictionaryCommentList.deleteComment, DictionaryCommentList, item, comment));
			}
			$('<div>',{'class':'dictionary_comment_date'}).text(item.written_date).appendTo(right_bot_div);
			$('<div>',{'class':'dictionary_comment_writer'}).text(gettext("작성자") + " : " + item.writer_nickname).appendTo(right_bot_div);

			$('<hr>',{'class': 'dictionary_comment_line'}).appendTo(comment);
	    });
	},
};

var IndexLectureList = {
	initialize:function()
	{
		this.semesters = $(".show_taken_lecture");
		this.lecture_lists = $(".taken_lecture_list");
		this.lecture_titles = $(".taken_lecture_title");
		this.registerHandles();
		this.current_open = this.semesters.length-1;
	},
	registerHandles:function()
	{
		$.each(this.semesters, function(index, item) {
			$(item).bind('click', $.proxyWithArgs(IndexLectureList.showLectures, IndexLectureList, item));
		});
	},
	showLectures:function(e, obj)
	{
		$(IndexLectureList.lecture_lists[IndexLectureList.current_open]).hide();
		$(IndexLectureList.lecture_titles[IndexLectureList.current_open]).find('td').css("background-color","#DFE0E4")
		IndexLectureList.current_open = parseInt(obj.id)-1;
		$(IndexLectureList.lecture_lists[IndexLectureList.current_open]).show();
		$(IndexLectureList.lecture_titles[IndexLectureList.current_open]).find('td').css("background-color","#C0D9FD");
	}
};

var IndexCommentList = {
	initialize:function()
	{
		this.comments = Data.Comments;
		this.timeline = $('#timeline');
		this.registerHandles();
		this.updateComment();
	},
	registerHandles:function()
	{
	},
	updateComment:function()
	{
		var max = NUM_ITEMS_PER_INDEX_COMMENT;
		$.ajax ({
			type: 'POST',
			url: '/dictionary/update_comment/',
			data: {'count': max,},
			dataType: 'json',
			success: function (resObj) {
				//try {
					if (resObj.result=='OK') {
						this.comments = resObj.comments;
						IndexCommentList.addToMultipleComment(resObj.comments)
					}
					else {
						Notifier.setErrrorMsg(gettext('오류가 발생했습니다.'));
					}
				//} catch (e) {
				//	Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
				//}	
			},
			error: function (xhr) {
                                if(suppress_ajax_errors)
                                    return;
				Notifier.setErrorMsg(gettext('오류가 발생했습니다.'));
			}
		});
	},

    addToMultipleComment:function(obj)
	{
		var total = $(obj).length;
		$.each(obj, function(index, item) {
			var div_comment = $('<div>', {'class': 'timeline_comment'});
			div_comment.appendTo(IndexCommentList.timeline);

			var left_div_comment = $('<div>', {'class': 'timeline_comment_left'});
			var right_div_comment = $('<div>', {'class': 'timeline_comment_right'});

			left_div_comment.appendTo(div_comment);
			right_div_comment.appendTo(div_comment);
			var prof_img=$('<img>', {'class': 'content_prof_photo', 'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+item.professor[0].professor_id+'.jpg'});
			img_existance(prof_img);
			prof_img.appendTo(left_div_comment);
			$('<div>', {'class': 'content_prof_name'}).text(item.professor[0].professor_name).appendTo(left_div_comment);
			var right_top_div = $('<div>', {'class': 'timeline_comment_right_top'});
			var right_top_div_title = $('<div>',{'class':'timeline_comment_right_top_title'});
			var right_top_div_spec = $('<div>',{'class':'timeline_comment_right_top_spec'});

			right_top_div.appendTo(right_div_comment);
			right_top_div_title.appendTo(right_top_div);
			right_top_div_spec.appendTo(right_top_div);

			var right_mid_div = $('<div>', {'class': 'timeline_comment_right_mid'});
			var right_mid_div_comment = $('<div>',{'class':'timeline_comment_right_mid_comment'});

			right_mid_div.appendTo(right_div_comment);
			right_mid_div_comment.appendTo(right_mid_div);

			var comment_output = item.comment

			$('<a>', {'class': 'content_subject','href':'view/'+item.course_code+"/"}).text(item.course_title).appendTo(right_top_div_title);
			$('<pre>', {'class': 'content_comment'}).text(comment_output).appendTo(right_mid_div_comment);

			var comment_eval = $('<div>', {'class': 'comment_eval'});
			$('<div>',{'class':'a_spec'}).text(gettext("학점 :")).appendTo(comment_eval);
			get_star_picture(item.score,comment_eval);
			$('<div>',{'class':'a_spec'}).text(gettext("로드 :")).appendTo(comment_eval);
			get_star_picture(item.load,comment_eval);
			$('<div>',{'class':'a_spec'}).text(gettext("남는거 :")).appendTo(comment_eval);
			get_star_picture(item.gain,comment_eval);
			comment_eval.appendTo(right_top_div_spec);

			var right_bot_div = $('<div>',{'class':'timeline_comment_right_bot'});
    		var right_bot_div_writer = $('<div>',{'class':'timeline_comment_right_bot_writer'});
    		var right_bot_div_date = $('<div>',{'class':'timeline_comment_right_bot_date'});

    		right_bot_div_writer.text('작성자 : '+ item.writer_nickname).appendTo(right_bot_div);
    		right_bot_div_date.text(item.written_date).appendTo(right_bot_div);
    		right_bot_div.appendTo(right_div_comment);
    		right_bot_div_date.appendTo(right_bot_div);
    		right_bot_div_writer.appendTo(right_bot_div);
			if (index != total -1){
				$('<hr>',{'class': 'comment_line'}).appendTo(IndexCommentList.timeline);
			}
	});
	}
};

var ProfessorCommentList = {
	initialize:function()
	{
		this.timeline = $('#course-comment-view');
		this.profInfo = $('#professor-info');
		this.registerHandles();
		this.showComment();
		this.onLoad();
	},
	onLoad:function()
	{
		this.addProfInfo();
	},
	registerHandles:function()
	{
	},
	clearProfInfo:function()
	{
		this.profInfo.empty();
	},
	addProfInfo:function()
	{
		var top_div = $('<div>', {'id': 'professor-info-top'});
		var bottom_div = $('<div>', {'id': 'professor-info-bottom'});
		top_div.appendTo(this.profInfo);
		bottom_div.appendTo(this.profInfo);

		var top_left_div = $('<div>', {'id': 'professor-info-left'});
		var prof_img = $('<img>', {'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+Data.Professor[0].professor_id+'.jpg'});
		img_existance(prof_img);
		prof_img.appendTo(top_left_div);
		top_left_div.appendTo(top_div);
		var top_right_div = $('<div>', {'id': 'professor-info-right'});
		top_right_div.appendTo(top_div);

        	var prof_name_line = $('<div>', {'class': 'professor_info_line'});
		$('<div>', {'id': 'professor-info-name-title'}).text(gettext("Name : " )).appendTo(prof_name_line);
		$('<div>', {'id': 'professor-info-name'}).text(Data.Professor[0].professor_name).appendTo(prof_name_line);
        	prof_name_line.appendTo(top_right_div);

        	var prof_major_line = $('<div>', {'class': 'professor_info_line'});
		$('<div>', {'id': 'professor-info-major-title'}).text(gettext("Major : " )).appendTo(prof_major_line);
		$('<pre>', {'id': 'professor-info-major'}).text(Data.ProfInfo.major).appendTo(prof_major_line);
        	$('<textarea>', {'id': 'professor-info-major-change'}).text(Data.ProfInfo.major).appendTo(prof_major_line);
        	prof_major_line.appendTo(top_right_div);

        	var prof_email_line = $('<div>', {'class': 'professor_info_line'});
		$('<div>', {'id': 'professor-info-email-title'}).text(gettext("E-mail : " )).appendTo(prof_email_line);
		$('<pre>', {'id': 'professor-info-email'}).text(Data.ProfInfo.email).appendTo(prof_email_line);
        	$('<textarea>', {'id': 'professor-info-email-change'}).text(Data.ProfInfo.email).appendTo(prof_email_line);
        	prof_email_line.appendTo(top_right_div);

        	var prof_homepage_line = $('<div>', {'class': 'professor_info_line'});
		$('<div>', {'id': 'professor-info-homepage-title'}).text(gettext("Homepage : " )).appendTo(prof_homepage_line);
		$('<pre>', {'id': 'professor-info-homepage'}).text(Data.ProfInfo.homepage).appendTo(prof_homepage_line);
        	$('<textarea>', {'id': 'professor-info-homepage-change'}).text(Data.ProfInfo.homepage).appendTo(prof_homepage_line);
        	prof_homepage_line.appendTo(top_right_div);
		var bottom_img = $('<div>', {'id': 'prof-info-bottom-img'});
		var change_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'prof-info-change-img'});
		var complete_img = $('<img>', {'src': Data.MediaUrl+'images/dictionary/fix.gif', 'id': 'prof-info-complete-img'});

        	var bottom_text = $('<div>', {'id': 'prof-info-change-user'});

        	if ( Data.ProfInfo.written_datetime != '')
		    bottom_text.text(gettext("마지막 고침 : ") + Data.ProfInfo.written_datetime+ " " + Data.ProfInfo.writer + " ");

		bottom_text.appendTo(bottom_div);
		change_img.appendTo(bottom_img);
		complete_img.appendTo(bottom_img);
		bottom_img.appendTo(bottom_div);
		change_img.bind('click', $.proxy(this.showProfInfo, this));
		complete_img.bind('click', $.proxy(this.changeProfInfo, this));

        $('#professor-info-major-change').hide();
        $('#professor-info-email-change').hide();
        $('#professor-info-homepage-change').hide();
        $('#prof-info-complete-img').hide();
	},
	showProfInfo:function()
	{
        $('#professor-info-major').hide();
        $('#professor-info-email').hide();
        $('#professor-info-homepage').hide();
        $('#prof-info-change-img').hide();
        $('#professor-info-major-change').show();
        $('#professor-info-email-change').show();
        $('#professor-info-homepage-change').show();
        $('#prof-info-complete-img').show();
	},
	changeProfInfo:function()
	{
        var new_major_content = $('#professor-info-major-change').val();
        var new_email_content = $('#professor-info-email-change').val();
        var new_homepage_content = $('#professor-info-homepage-change').val();
        var prof_id = Data.Professor[0].professor_id;
        var conditions = { 'major': new_major_content, 'email': new_email_content, 'homepage': new_homepage_content, 'prof_id': prof_id};

        $.ajax({
            type: 'POST',
            url: '/dictionary/add_professor_info/',
            data: conditions,
            dataType: 'json',
            success: $.proxy(function(resObj){
                try {
                    if (resObj.result == 'OK') {
                        Data.ProfInfo = resObj.prof_info;
			this.clearProfInfo();
			this.addProfInfo();
                    }else{
                    }
                } catch(e) {
                    Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
                }
            }, this),
            error: function(xhr){
                if (suppress_ajax_errors)
                    return;
                if (xhr.status == 403){
                    Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
                }
            }
        });

        $('#professor-info-major').text(new_major_content);
        $('#professor-info-email').text(new_email_content);
        $('#professor-info-homepage').text(new_homepage_content);
        $('#professor-info-major').show();
        $('#professor-info-email').show();
        $('#professor-info-homepage').show();
        $('#prof-info-change-img').show();
        $('#professor-info-major-change').hide();
        $('#professor-info-email-change').hide();
        $('#professor-info-homepage-change').hide();
        $('#prof-info-complete-img').hide();
	},
	showComment:function()
	{
		var max = NUM_ITEMS_PER_PROF_COMMENT;
        var prof_id = Data.Professor[0].professor_id
		var conditions = {'count': max, 'prof_id': prof_id};
		$.ajax ({
			type: 'POST',
			url: '/dictionary/professor_comment/',
			data: conditions,
			dataType: 'json',
			success: function (resObj) {
				try {
					if (resObj.result=='OK') {
						ProfessorCommentList.addToMultipleComment(resObj.comments)
					}
					else {
						Notifier.setErrrorMsg(gettext('오류가 발생했습니다.'));
					}
				} catch (e) {
                                    Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}	
			},
			error: function (xhr) {
                                if (suppress_ajax_errors)
                                        return;
				Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
			}
		});
	},
	addToMultipleComment:function(obj)
	{
                var total = $(obj).length;
		$.each(obj, function(index, item) {
			var div_comment = $('<div>', {'class': 'professor_comment'});
			div_comment.appendTo(ProfessorCommentList.timeline);

                        var top_div = $('<div>',{'class': 'professor_comment_top'});
                        var top_div_title = $('<div>',{'class':'professor_comment_top_title'});
                        var top_div_spec = $('<div>',{'class':'professor_comment_top_spec'});

                        top_div.appendTo(div_comment);
                        top_div_title.appendTo(top_div);
                        top_div_spec.appendTo(top_div);

                        var mid_div = $('<div>', {'class': 'professor_comment_mid'});

                        mid_div.appendTo(div_comment);

                        var comment_output = item.comment

                        $('<span>', {'class' : 'content_subject'}).text("<"+item.year+" "+(item.semester==1?"봄":"가을")+"학기> ").appendTo(top_div_title);
                        $('<a>', {'class' : 'content_subject', 'href':'/dictionary/view/'+item.course_code+"/"}).text(item.course_title).appendTo(top_div_title);
                        $('<pre>', {'class': 'professor_content_comment'}).text(comment_output).appendTo(mid_div);

			var comment_eval = $('<div>', {'class': 'comment_eval'});
			$('<div>',{'class':'a_spec'}).text(gettext("학점 :")).appendTo(comment_eval);
			get_star_picture(item.score,comment_eval);
			$('<div>',{'class':'a_spec'}).text(gettext("로드 :")).appendTo(comment_eval);
			get_star_picture(item.load,comment_eval);
			$('<div>',{'class':'a_spec'}).text(gettext("남는거 :")).appendTo(comment_eval);
			get_star_picture(item.gain,comment_eval);
			comment_eval.appendTo(top_div_spec);

                        var bot_div = $('<div>',{'class':'professor_comment_bot'});
                        var bot_div_writer = $('<div>',{'class':'professor_comment_bot_writer'});
                        var bot_div_date = $('<div>',{'class':'professor_comment_bot_date'});

                        bot_div_writer.text('작성자 : '+ item.writer_nickname).appendTo(bot_div);
                        bot_div_date.text(item.written_date).appendTo(bot_div);

                        bot_div.appendTo(div_comment);
                        bot_div_date.appendTo(bot_div);
                        bot_div_writer.appendTo(bot_div);

                        if (index != total -1){
                            $('<hr>',{'class': 'professor_comment_line'}).appendTo(ProfessorCommentList.timeline);
                        }
		});
	}
}

var FavoriteList = {
	initialize:function()
	{
		this.favorites = $('#favorite_view_contents');
		this.total = $(Data.Favorites).length;
		this.addToMultipleFavorite(Data.Favorites);
	},
	showEmptyNotice:function()
	{
		var notice = $('<div>', {'class': 'dictionary_favorite_empty'}).text('추가해 주세요');
		notice.appendTo(this.favorites);
	},
	addToMultipleFavorite:function(obj)
	{
		if(this.total == 0){
			this.showEmptyNotice();
		}
		$.each(obj, function(index, item) {
			var favorite = $('<div>', {'class': 'dictionary_favorite'});
			var favorite_name = $('<div>', {'class': 'dictionary_favorite_name'});
			favorite.appendTo(FavoriteList.favorites);
			favorite_name.appendTo(favorite);
			$('<a>', {'href': item.url}).text(item.code + ' - ' + item.title).appendTo(favorite_name);
			var deletelink = $('<img>', {'class': 'dictionary_favorite_delete','src':Data.MediaUrl+'images/dictionary/x_sign.jpg'});
			deletelink.appendTo(favorite);
			deletelink.bind('click', $.proxyWithArgs(FavoriteList.deleteFavorite, FavoriteList, item, favorite));
		});
	},
	deleteFavorite:function(e,obj, favorite) 
	{
		$.ajax({
			type: 'POST',
			url: '/dictionary/delete_favorite/',
			data: {'course_id': obj.course_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='DELETE') {
                        favorite.remove();
						this.total--;
						if(this.total==0){
							this.showEmptyNotice();
						}
					} else if (resObj=='REMOVE_NOT_EXIST') {
						Notifier.setErrorMsg(gettext('잘못된 접근입니다.'));
					}
				}
				catch(e) {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			}, this),
			error: function(xhr) {
				if (suppress_ajax_errors)
					return;
				if (xhr.status == 403) {
					Notifier.setErrorMsg(gettext('로그인해야 합니다.'));
				}
				else {
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+gettext('요청 실패')+':'+xhr.status+')');
				}
			}
		});
	}
};

var FavoriteController = {
	initialize:function()
	{
		this.course_id =  Data.Course['id'];
		this.submitFavorite = $('input[name="addFavorite"]');
		this.registerHandles();
	},
	registerHandles:function()
	{
		$(this.submitFavorite).bind('click', $.proxy(this.addFavorite, this));

	},
	addFavorite:function(obj)
	{
		$.ajax({
			type: 'POST', 
			url: '/dictionary/add_favorite/',
			data: {'course_id': this.course_id},
			dataType: 'json',
			success: $.proxy(function(resObj) {
				try {
					if (resObj.result=='ADD') {
						Notifier.setErrorMsg(gettext('추가되었습니다.'));
					} else if (resObj.result='ALREADY_ADDED') {
						Notifier.setErrorMsg(gettext('이미 추가하셨습니다.'));
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

};

var RecommendController = {
	initialize:function()
	{
		this.courses = [];
		this.recommendArea=$('#recommend-area-professors');
		this.getRecommend(this);
	},
	getRecommend:function(obj)
	{
		$.ajax({
			type:'GET',
			url: '/dictionary/get_recommend/',
			dataType:'json',
			success: $.proxy(function(resObj) {
				try{
					obj.courses = resObj.courses_sorted;
					this.addToMultipleRecommend(resObj.courses_sorted);
				}
				catch(e){
					Notifier.setErrorMsg(gettext('오류가 발생하였습니다.')+' ('+e.message+')');
				}
			},this),
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
	addToMultipleRecommend:function(obj)
	{
		var total = $(obj).length;
		$.each(obj, function(index,item) {
			var div_recommend = $('<div>',{'class':'recommend_subject'});
			var div_recommend_a = $('<a>',{'href':'/dictionary/view/'+item.course_code});
			var div_recommend_image = $('<img>',{'src':'http://cais.kaist.ac.kr/static_files/photo/1990/'+item.professor_id+'.jpg','class':'content_prof_photo'});
			img_existance(div_recommend_image);
			var div_recommend_subject_code = $('<div>',{'class':'recommend_subject_code'}).text(item.course_code);
			var div_recommend_subject_title = $('<div>',{'class':'recommend_subject_title'}).text(item.course_title);
			var course_title = ''
			if (item.course_title.length > 14)
				course_title = item.course_title.substring(0,14) + "..";
			else 
				course_title = item.course_title;
			var div_recommend_subject_title = $('<div>',{'class':'recommend_subject_title'}).text(course_title);
			var div_recommend_profname = $('<div>',{'class':'recommend_subject_profname'}).text(item.professor_name);
			div_recommend_a.appendTo(div_recommend);
			div_recommend_image.appendTo(div_recommend_a);
			div_recommend_subject_code.appendTo(div_recommend_a);
			div_recommend_subject_title.appendTo(div_recommend_a);
			div_recommend_profname.appendTo(div_recommend_a);
			div_recommend.appendTo(RecommendController.recommendArea);	
		});
	}
};
