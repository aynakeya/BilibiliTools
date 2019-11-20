var coll = new Array();
var collt = new Array();
var page = 1;
var totalpages = 17;
var amount = 0;
function abc (event) {
	var evt = event.keyCode;
	if (evt == 13) 
	{
		h = setTimeout(bcd, 1000);
	}
}
function bcd()
{
	var a = document.getElementsByClassName("title");
	for (var i=0;i<a.length;i++)
	{
		coll[amount] = a[i].href;
		collt[amount] = a[i].innerText;
		amount = amount + 1;
	}
	alert("done");
}

onkeypress="abc(event)"
id="inputpage"