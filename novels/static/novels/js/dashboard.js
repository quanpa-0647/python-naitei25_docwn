$(document).ready(function () {
  const novelLabels = [];
  const novelData = [];
  const today = new Date();

  for (let i = 29; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    const label = d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
    novelLabels.push(label);
    novelData.push(Math.floor(Math.random() * 10)); 
  }

  const $novelCtx = $('#novelChart');
  if ($novelCtx.length) {
    const novelChart = new Chart($novelCtx[0].getContext('2d'), {
      type: 'line',
      data: {
        labels: novelLabels,
        datasets: [{
          label: 'Số tiểu thuyết mới',
          data: novelData,
          fill: true,
          backgroundColor: 'rgba(54, 162, 235, 0.2)',
          borderColor: '#36A2EB',
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: {
            ticks: { maxTicksLimit: 10 }
          },
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Số lượng'
            }
          }
        }
      }
    });
  }

  const $userCtx = $('#userChart');
  if ($userCtx.length) {
    const userChart = new Chart($userCtx[0].getContext('2d'), {
      type: 'bar',
      data: {
        labels: window.chartLabels || [],
        datasets: [{
          label: 'Số lượng người dùng',
          data: window.chartData || [],
          backgroundColor: 'rgba(54, 162, 235, 0.6)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              stepSize: 1
            }
          }
        }
      }
    });
  }
});
