function clockHandler () {
    function updateDigitalWatch() {
        const digitalWatch = document.getElementById('digitalWatch');
        const currentTime = new Date();
        const hours = currentTime.getHours().toString().padStart(2, '0');
        const minutes = currentTime.getMinutes().toString().padStart(2, '0');
        const seconds = currentTime.getSeconds().toString().padStart(2, '0');
        const timeString = `${hours}:${minutes}:${seconds}`;
        digitalWatch.innerText = timeString;
      }
      
      setInterval(updateDigitalWatch, 1000);
}
export default  clockHandler;