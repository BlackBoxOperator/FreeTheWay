var liffID = '1655616509-K5V7eoER';

liff.init({
  liffId: liffID
}).then(function() {
  console.log('LIFF init');

  // 這邊開始寫使用其他功能

}).catch(function(error) {
  console.log(error);
});

function cctvChange(){
}

function cctv_box(){
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
  if ( !instance.dtbox ) return;
  if ( instance.dtbox.visible ) return;
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
      if(prev_date === null || prev_time === null) return;

      date = new Date(instance.dtbox.year, instance.dtbox.month, instance.dtbox.day, instance.dtbox.hours, instance.dtbox.minutes);
      date.setHours(date.getHours() + 1);
      instance.dtbox.value = date;
      instance.dtbox.year = date.getFullYear();
      instance.dtbox.month = date.getMonth();
      instance.dtbox.day = date.getDate();
      instance.dtbox.hours = date.getHours();
      instance.dtbox.minutes = date.getMinutes();
      instance.dtbox.seconds = date.getSeconds();
      instance.dtbox.setInputValue()
      updatePrev(true);
    } else {
      /* right swipe */
      if(prev_date === null || prev_time === null) return;
      date = new Date(instance.dtbox.year, instance.dtbox.month, instance.dtbox.day, instance.dtbox.hours, instance.dtbox.minutes);
      date.setHours(date.getHours() - 1);
      instance.dtbox.value = date;
      instance.dtbox.year = date.getFullYear();
      instance.dtbox.month = date.getMonth();
      instance.dtbox.day = date.getDate();
      instance.dtbox.hours = date.getHours();
      instance.dtbox.minutes = date.getMinutes();
      instance.dtbox.seconds = date.getSeconds();
      instance.dtbox.setInputValue()
      updatePrev(true);
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
  if(!instance.dtbox) return;
  instance.dtbox.value = value;
  instance.dtbox.year = value.getFullYear();
  instance.dtbox.month = value.getMonth();
  instance.dtbox.day = value.getDate();
  instance.dtbox.hours = value.getHours();
  instance.dtbox.minutes = value.getMinutes();
  instance.dtbox.seconds = value.getSeconds();
  instance.dtbox.setInputValue()
}

var begLoc = "";
var endLoc = "";
var instance = null;
var prev_date = null;
var prev_time = null;

function bmbRemoveClass(s){
    return s.removeClass("bmb_rd_80plus")
     .removeClass("bmb_rd_60_80")
     .removeClass("bmb_rd_40_60")
     .removeClass("bmb_rd_20_40")
     .removeClass("bmb_rd_0_20")
     .removeClass("bmb_rd_closure")
     .removeClass("bmb_rd_noinfo")
}

function updatePrev(change){
  if(instance.dtbox.value)
    prev_date = instance.dtbox.value;
  prev_time = instance.dtbox.time;

  console.log(change);
  if(prev_time !== null && prev_date !== null && change){
    instance.dtbox.setInputValue();
    // do ajax
    console.log("do ajax");
    //$.post(`${window.location.host}`)

    time = `${instance.dtbox.month + 1}/${instance.dtbox.day} ${instance.dtbox.hours}:${instance.dtbox.minutes}`;
    $.ajax({
      url: 'http://localhost:8080/traffic',
      type: 'post',
      data: JSON.stringify({
        time: time,
      }),
      dataType: 'json',
      contentType: 'application/json',
      success: function (data) {

        lv = ["bmb_rd_80plus", "bmb_rd_60_80", "bmb_rd_40_60"]

        Object.keys(data.N).forEach(k => {
          name = k.replace('交流道', '')
          bmbRemoveClass($($(`#${name}`).parent().prev().find('.bmb_rd')[0])).addClass(lv[data.N[k].level - 1])
        })

        Object.keys(data.S).forEach(k => {
          name = k.replace('交流道', '')
          bmbRemoveClass($($(`#${name}`).parent().next().find('.bmb_rd')[1])).addClass(lv[data.S[k].level - 1])
        })
      },
      error: function(){
        console.log(time);
      }
    });

  }
}

document.onreadystatechange = () => {
  if (document.readyState === 'complete') {

    //$('.bmb_rd')
    //  .removeClass("bmb_rd_80plus")
    //  .removeClass("bmb_rd_60_80")
    //  .removeClass("bmb_rd_40_60")
    //  .removeClass("bmb_rd_20_40")
    //  .removeClass("bmb_rd_0_20")
    //  .removeClass("bmb_rd_closure")

    //$('.bmb_rd').addClass("bmb_rd_noinfo").text('');

    instance = new dtsel.DTS('input[name="dateTimePicker"]',  {
      direction: 'BOTTOM',
      dateFormat: "yyyy-mm-dd",
      showTime: true,
      timeFormat: "HH:MM"
    });

    //setTime(new Date());
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the button that opens the modal

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    $("#reportButton").click(function(){
      if(!instance.dtbox){
        alert("未選擇時間");
      }
      else if(!begLoc){
        alert("未設定起始站，請點選站點");
      }
      else if(!endLoc){
        alert("未設定終點站，請點選站點");
      }
      else{
        confirm(`申報 ${begLoc} 到 ${endLoc}？`);
      }
    })

    function dateTimeHandler(state, prevState) {
      //if (state.visible && !prevState.visible){})
      var change = false;
      if(state && state.visible) return;
      if(prev_time === null || prev_date === null){
        change = true;
        console.log("onchange; from null");
        //console.log('date', prev_date.getTime());
        //console.log('time', prev_time);
        if(instance.dtbox.value)
          console.log(instance.dtbox.value.getTime());
        console.log(instance.dtbox.time);
      }
      else if(prev_date !== null &&
        (prev_date.getTime() != instance.dtbox.value.getTime()
          || prev_time !== null && prev_time != instance.dtbox.time)){
        change = true;
        console.log("onchange;");
        console.log('date', prev_date ? prev_date.getTime() : 'no date');
        console.log('time', prev_time);
        console.log(instance.dtbox.value.getTime());
        console.log(instance.dtbox.time);
      }
      else{
        console.log("no onchange;");
        if(prev_time !== null)
          console.log('time', prev_time);
        if(prev_date !== null)
          console.log('date', prev_date.getTime());
        console.log(instance.dtbox.value.getTime());
        console.log(instance.dtbox.time);
      }

      updatePrev(change);
    }

    instance.dtbox.addHandler("value", dateTimeHandler)

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
      modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
      if (event.target == modal) {
        modal.style.display = "none";
      }

      if (!$(event.target).hasClass("cal-cell") &&
        !$(event.target).hasClass("cal-nav") &&
        !$(event.target).hasClass("cal-time-label") &&
        !$(event.target).hasClass("dateTimePicker") ) {
        if(instance.dtbox){
          instance.dtbox.visible = false;
          dateTimeHandler();
        }
      }
    }

    $('#setBegBtn').click(function(){
      var modal = document.getElementById("myModal");
      modal.style.display = "none";
      if(begLoc) $('#' + begLoc).removeClass('active');
      begLoc = $('#modal-loc').text();
      $('#' + begLoc).addClass('active');
    })

    $('#setEndBtn').click(function(){
      var modal = document.getElementById("myModal");
      modal.style.display = "none";
      if(endLoc) $('#' + endLoc).removeClass('active');
      endLoc = $('#modal-loc').text();
      $('#' + endLoc).addClass('active');
    })

    $('#setNonBtn').click(function(){
      var modal = document.getElementById("myModal");
      modal.style.display = "none";
      if(endLoc == $('#modal-loc').text()){
        $('#' + endLoc).removeClass('active');
        endLoc = "";
      }
      if(begLoc == $('#modal-loc').text()){
        $('#' + begLoc).removeClass('active');
        begLoc = "";
      }
    })
  }
};

// When the user clicks the button, open the modal
function getToFind(val, id, loc, sec){
  if(!sec){
    $('#modal-loc').text(loc);
    var modal = document.getElementById("myModal");
    modal.style.display = "block";
  }
}

function Change(){
}
