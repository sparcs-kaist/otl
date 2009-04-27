document.addEvent('domready', function() {
	new PhotoFlow($('photoflow'), [
		'/media/images/about/meeting-whiteboard1.jpg',
		'/media/images/about/meeting-sparcsroom.jpg',
		'/media/images/about/meeting-sparcsroom2.jpg'
	], [
		'가장 처음 아이디어 회의 때...',
		'조모임 보드 회의 때...',
		'회의 장면. 겉보기엔 재밌어(?) 보이지만 서로 간의 생각 차이를 좁히기 위한 무한 토론의 시간.<br/>대충 OTL 프로젝트의 컨셉을 다 잡기까지 일주일이 넘게 걸렸던 것 같다.'
	]);
});
