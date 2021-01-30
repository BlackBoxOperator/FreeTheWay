var liffID = 'https://liff.line.me/1655616509-ldoQx2kG';
var profile = null;
/*
{
  "userId": "U4af4980629...",
  "displayName": "Brown",
  "pictureUrl": "https://profile.line-scdn.net/abcdefghijklmn",
  "statusMessage": "Hello, LINE!"
}
*/

liff.init({
  liffId: liffID
}).then(function() {
  console.log('LIFF init');
  profile = liff.getProfile()
  $.ajax({
    url: `${window.location.origin}/reported`,
    type: 'post',
    data: JSON.stringify({
      userid: profile.userId,
    }),
    dataType: 'json',
    contentType: 'application/json',
    success: function (data) {
      // map data
      data.forEach(d => {
        $(`#list`).append(`<li class="list-group-item">${d.reportid} ${d.start} ${d.end} ${d.time}</li>`);
      });
    },
    error: function(){
      alert("error");
    }
  });
}).catch(function(error) {
  console.log(error);
});

$(document).ready(function(){

  $('#reg').click(function(){
    $.ajax({
      url: `${window.location.origin}/register`,
      type: 'post',
      data: JSON.stringify({
        userid: profile.userId,
        carid: profile.userId,
      }),
      dataType: 'json',
      contentType: 'application/json',
      success: function (data) {
        alert(data.message);
      },
      error: function(){
        alert("error");
      }
    });
  })
})
