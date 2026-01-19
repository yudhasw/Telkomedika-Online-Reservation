const passwordInput = document.getElementById('password');
const bars = [
    document.getElementById('bar-1'),
    document.getElementById('bar-2'),
    document.getElementById('bar-3'),
    document.getElementById('bar-4'),
    document.getElementById('bar-5')
];

passwordInput.addEventListener('input', function() {
    const val = this.value;
    const len = val.length;

    bars.forEach(bar => bar.className = 'h-1.5 w-full bg-gray-200 rounded-full transition-colors duration-300');

    if (len > 0) bars[0].classList.replace('bg-gray-200', 'bg-red-400');
    if (len > 3) bars[1].classList.replace('bg-gray-200', 'bg-orange-400');
    if (len > 5) bars[2].classList.replace('bg-gray-200', 'bg-yellow-400');
    if (len > 7) bars[3].classList.replace('bg-gray-200', 'bg-lime-400');
    if (len > 9) bars[4].classList.replace('bg-gray-200', 'bg-green-500');
});

var date = new Date();
var tdate = date.getDate();
var month = date.getMonth() + 1;
if (tdate < 10) {
    tdate = "0" + tdate;
}
if (month < 10) {
    month = "0" + month;
}
var year = date.getUTCFullYear();
var maxDate = year + "-" + month + "-" + tdate;
document.getElementById("tanggal_lahir").setAttribute('max', maxDate);