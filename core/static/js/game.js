const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Cargar imágenes
const bg = new Image();
bg.src = 'assets/fondo.png';

const skaterImages = [new Image(), new Image()];
skaterImages[0].src = 'assets/skater4.png';
skaterImages[1].src = 'assets/skater2.png';

const skaterJump = new Image();
skaterJump.src = 'assets/skaterjump.png';

const cone = new Image();
cone.src = 'assets/cono.png';
const trashcan = new Image();
trashcan.src = 'assets/basurero.png';


let bgX = 0;
let gravity = 1;
let jumpPower = 18;
let isJumping = false;
let score = 0;
let gameSpeed = 6;
let skaterFrame = 0;
let frameCount = 0;
let gameOver = false;

// Jugador
const player = {
  x: 100,
  y: 300,
  width: 50,
  height: 50,
  velocityY: 0,
  draw() {
    if (isJumping) {
      ctx.drawImage(skaterJump, this.x, this.y, this.width, this.height);
    } else {
      ctx.drawImage(skaterImages[skaterFrame], this.x, this.y, this.width, this.height);
    }
  },
  update() {
    this.y += this.velocityY;
  
    if (this.y < 300) {
      this.velocityY += gravity;
      isJumping = true;
    } else {
      this.velocityY = 0;
      this.y = 300;
      isJumping = false;
    }
  
    if (!isJumping) {
      frameCount++;
      if (frameCount % 10 === 0) {
        skaterFrame = (skaterFrame + 1) % 2;
      }
    }
  }
  
};

// Obstáculo
const obstacle = {
  x: 800,
  y: 310,
  width: 30,
  height: 50,
  draw() {
    ctx.drawImage(cone, this.x, this.y, this.width, this.height);
  },
  update() {
    this.x -= gameSpeed;
    if (this.x + this.width < 0) {
      this.x = 800 + Math.random() * 400;
      score++;
    }
  }
};
const obstacle2 = {
  x: 1200,
  y: 310,
  width: 40,
  height: 50,
  draw() {
    ctx.drawImage(trashcan, this.x, this.y, this.width, this.height);
  },
  update() {
    this.x -= gameSpeed;
    if (this.x + this.width < 0) {
      this.x = 800 + Math.random() * 600;
      score++;
    }
  }
};


// Input
window.addEventListener('keydown', function (e) {
  if (e.code === 'Space' && !isJumping && !gameOver) {
    player.velocityY = -jumpPower;
    isJumping = true;
  }
});

// Mostrar pantalla Game Over
function showGameOver() {
  gameOver = true;
  document.getElementById('finalScore').textContent = 'Puntaje final: ' + score;
  document.getElementById('gameOverScreen').style.display = 'flex';
}

// Reiniciar juego
function restartGame() {
  document.location.reload();
}

// Bucle principal
function gameLoop() {
  if (gameOver) return;

  // Fondo en movimiento
  bgX -= 2;
  if (bgX <= -canvas.width) bgX = 0;
  ctx.drawImage(bg, bgX, 0, canvas.width, canvas.height);
  ctx.drawImage(bg, bgX + canvas.width, 0, canvas.width, canvas.height);

  player.update();
  player.draw();

  obstacle.update();
  obstacle.draw();

  obstacle2.update();
  obstacle2.draw();


  // Detección de colisión
  if (
    player.x < obstacle.x + obstacle.width &&
    player.x + player.width > obstacle.x &&
    player.y < obstacle.y + obstacle.height &&
    player.y + player.height > obstacle.y
  ) {
    showGameOver();
    return;
  }
  if (
    player.x < obstacle2.x + obstacle2.width &&
    player.x + player.width > obstacle2.x &&
    player.y < obstacle2.y + obstacle2.height &&
    player.y + player.height > obstacle2.y
  ) {
    showGameOver();
    return;
  }
  

  // Puntaje
  ctx.fillStyle = 'white';
  ctx.font = '24px monospace';
  ctx.fillText('Puntaje: ' + score, 20, 30);

  requestAnimationFrame(gameLoop);
}

gameLoop();

document.getElementById('jumpBtn').addEventListener('click', () => {
  if (!isJumping && !gameOver) {
    player.velocityY = -jumpPower;
    isJumping = true;
  }
});

