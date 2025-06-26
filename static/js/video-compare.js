document.addEventListener('DOMContentLoaded', function() {
    const containers = document.querySelectorAll('.video-compare-container');
    
    containers.forEach(container => {
        const slider = container.querySelector('.slider');
        const beforeVideo = container.querySelector('.video-before video');
        const afterVideo = container.querySelector('.video-after video');
        let isResizing = false;

        // 鼠标悬停时播放视频
        container.addEventListener('mouseenter', function() {
            if (!isResizing) {  // 只有在不拖动时才播放
                beforeVideo.play();
                afterVideo.play();
            }
        });

        // 鼠标离开时暂停视频
        container.addEventListener('mouseleave', function() {
            beforeVideo.pause();
            afterVideo.pause();
        });

        // 确保视频时间同步
        beforeVideo.addEventListener('timeupdate', () => {
            if (Math.abs(beforeVideo.currentTime - afterVideo.currentTime) > 0.1) {
                afterVideo.currentTime = beforeVideo.currentTime;
            }
        });

        // 滑块拖动功能
        slider.addEventListener('mousedown', (e) => {
            isResizing = true;
            // 暂停两个视频
            beforeVideo.pause();
            afterVideo.pause();
            e.preventDefault();
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const containerRect = container.getBoundingClientRect();
            let position = (e.pageX - containerRect.left) / containerRect.width * 100;
            
            // 限制滑块在容器内
            position = Math.max(0, Math.min(100, position));

            slider.style.left = `${position}%`;
            container.querySelector('.video-before').style.clipPath = 
                `polygon(0 0, ${position}% 0, ${position}% 100%, 0 100%)`;
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                // 检查鼠标是否还在容器内
                const mouseX = event.clientX;
                const mouseY = event.clientY;
                const containerRect = container.getBoundingClientRect();
                const isMouseInContainer = 
                    mouseX >= containerRect.left && 
                    mouseX <= containerRect.right && 
                    mouseY >= containerRect.top && 
                    mouseY <= containerRect.bottom;

                if (isMouseInContainer) {
                    // 如果鼠标还在容器内，恢复播放
                    beforeVideo.play();
                    afterVideo.play();
                }
            }
        });

        // 初始化视频显示区域
        container.querySelector('.video-before').style.clipPath = 'polygon(0 0, 50% 0, 50% 100%, 0 100%)';
        slider.style.left = '50%';
    });
}); 