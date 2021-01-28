var liffID = '1655616509-K5V7eoER';

//liff.init({
//  liffId: liffID
//}).then(function() {
//  console.log('LIFF init');
//
//  // 這邊開始寫使用其他功能
//
//}).catch(function(error) {
//  console.log(error);
//});

//$(document).ready(function(){
//  instance = new dtsel.DTS('input[name="dateTimePicker"]',  {
//    direction: 'BOTTOM',
//    dateFormat: "yyyy-mm-dd",
//    showTime: true,
//    timeFormat: "HH:MM:SS"
//  });
//})

function getToFind(){
}

function cctvChange(){
}

document.addEventListener('touchstart', handleTouchStart, false);
document.addEventListener('touchmove', handleTouchMove, false);

var xDown = null;
var yDown = null;

function getTouches(evt) {
  return evt.touches ||             // browser API
    evt.originalEvent.touches; // jQuery
}

function handleTouchStart(evt) {
  const firstTouch = getTouches(evt)[0];
  xDown = firstTouch.clientX;
  yDown = firstTouch.clientY;
};

function handleTouchMove(evt) {
  if ( ! xDown || ! yDown ) {
    return;
  }

  var xUp = evt.touches[0].clientX;
  var yUp = evt.touches[0].clientY;

  var xDiff = xDown - xUp;
  var yDiff = yDown - yUp;

  if ( Math.abs( xDiff ) > Math.abs( yDiff ) ) {/*most significant*/
    if ( xDiff > 0 ) {
      /* left swipe */
      instance.dtbox.hours += 1;
      if(instance.dtbox.hours == 0)
        instance.dtbox.day += 1;
      instance.dtbox.setInputValue()
    } else {
      /* right swipe */
      instance.dtbox.hours -= 1;
      if(instance.dtbox.hours == -1)
        instance.dtbox.day -= 1;
      instance.dtbox.setInputValue()
    }
  } else {
    if ( yDiff > 0 ) {
      //alert("up")
      /* up swipe */
    } else {
      //alert("down")
      /* down swipe */
    }
  }
  /* reset values */
  xDown = null;
  yDown = null;
};

function setTime(date){
  var value = date;
  instance.dtbox.value = value;
  instance.dtbox.year = value.getFullYear();
  instance.dtbox.month = value.getMonth();
  instance.dtbox.day = value.getDate();
  instance.dtbox.hours = value.getHours();
  instance.dtbox.minutes = value.getMinutes();
  instance.dtbox.seconds = value.getSeconds();
  instance.dtbox.setInputValue()
}

document.onreadystatechange = () => {
  if (document.readyState === 'complete') {
    setTime(new Date());
  }
};
