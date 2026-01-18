import { useState, useEffect, useRef } from 'react'

const generateQuestion = (level) => {
  const operations = ['+', '-', '*', '/']
  let question, answer

  if (level <= 3) {
    // Simple operations
    const a = Math.floor(Math.random() * 20) + 1
    const b = Math.floor(Math.random() * 20) + 1
    const op = operations[Math.floor(Math.random() * operations.length)]

    if (op === '/') {
      // Ensure clean division
      const divisor = Math.floor(Math.random() * 10) + 1
      const result = Math.floor(Math.random() * 10) + 1
      question = `${divisor * result} ${op} ${divisor}`
      answer = result
    } else {
      question = `${a} ${op} ${b}`
      answer = eval(question)
    }
  } else if (level <= 6) {
    // Two operations
    const a = Math.floor(Math.random() * 15) + 1
    const b = Math.floor(Math.random() * 15) + 1
    const c = Math.floor(Math.random() * 15) + 1
    const op1 = operations[Math.floor(Math.random() * operations.length)]
    const op2 = operations[Math.floor(Math.random() * operations.length)]

    question = `${a} ${op1} ${b} ${op2} ${c}`
    answer = Math.round(eval(question) * 100) / 100
  } else {
    // BODMAS with parentheses
    const a = Math.floor(Math.random() * 10) + 1
    const b = Math.floor(Math.random() * 10) + 1
    const c = Math.floor(Math.random() * 10) + 1
    const d = Math.floor(Math.random() * 10) + 1
    const op1 = operations[Math.floor(Math.random() * operations.length)]
    const op2 = operations[Math.floor(Math.random() * operations.length)]
    const op3 = operations[Math.floor(Math.random() * operations.length)]

    question = `(${a} ${op1} ${b}) ${op2} ${c} ${op3} ${d}`
    answer = Math.round(eval(question) * 100) / 100
  }

  return { question, answer: answer.toString() }
}

const generateOptions = (correctAnswer, level) => {
  const correct = parseFloat(correctAnswer)
  const options = [correct]

  // Generate 3 wrong answers
  const range = level <= 3 ? 10 : level <= 6 ? 20 : 30

  while (options.length < 4) {
    let wrongAnswer
    const variation = Math.floor(Math.random() * range) + 1

    // Random type of wrong answer
    const wrongType = Math.floor(Math.random() * 4)
    switch (wrongType) {
      case 0:
        wrongAnswer = correct + variation
        break
      case 1:
        wrongAnswer = correct - variation
        break
      case 2:
        wrongAnswer = correct * 2
        break
      default:
        wrongAnswer = Math.max(1, correct - variation * 2)
    }

    wrongAnswer = Math.round(wrongAnswer * 100) / 100

    // Don't add duplicates
    if (!options.includes(wrongAnswer) && wrongAnswer !== correct) {
      options.push(wrongAnswer)
    }
  }

  // Shuffle options
  return options.sort(() => Math.random() - 0.5)
}

const getTimeLimit = (level) => {
  // Start at 30 seconds, decrease by 3 seconds per level, minimum 10 seconds
  return Math.max(10, 30 - (level - 1) * 3)
}

function App() {
  const [level, setLevel] = useState(1)
  const [score, setScore] = useState(0)
  const [lives, setLives] = useState(3)
  const [currentQuestion, setCurrentQuestion] = useState(null)
  const [options, setOptions] = useState([])
  const [selectedAnswer, setSelectedAnswer] = useState(null)
  const [feedback, setFeedback] = useState('')
  const [gameOver, setGameOver] = useState(false)
  const [playerPosition, setPlayerPosition] = useState(0)
  const [timeLeft, setTimeLeft] = useState(30)
  const [isAnswering, setIsAnswering] = useState(false)
  const [dragonAttack, setDragonAttack] = useState(false)
  const [wrongAnswersInLevel, setWrongAnswersInLevel] = useState(0)
  const [isShooting, setIsShooting] = useState(false)
  const [dragonFalling, setDragonFalling] = useState(false)
  const timerRef = useRef(null)
  const startTimeRef = useRef(null)

  // Generate new question
  const newQuestion = (currentLevel) => {
    const q = generateQuestion(currentLevel)
    setCurrentQuestion(q)
    setOptions(generateOptions(q.answer, currentLevel))
    setTimeLeft(getTimeLimit(currentLevel))
    setSelectedAnswer(null)
    setIsAnswering(false)
    startTimeRef.current = Date.now()
  }

  useEffect(() => {
    newQuestion(level)
  }, [level])

  // Timer countdown
  useEffect(() => {
    if (isAnswering || !currentQuestion || feedback) return

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current)
          handleTimeout()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timerRef.current)
  }, [currentQuestion, isAnswering, feedback])

  const handleTimeout = () => {
    setDragonAttack(true)
    setIsAnswering(true)

    setTimeout(() => {
      const newWrongCount = wrongAnswersInLevel + 1
      setWrongAnswersInLevel(newWrongCount)
      setLives(lives - 1)

      if (newWrongCount >= 2) {
        // Second wrong answer (timeout) in this level - game over
        setFeedback(`⏰ Dragon got Mario! The answer was ${currentQuestion.answer}. You used your second chance - Game Over!`)
        setTimeout(() => setGameOver(true), 2000)
      } else {
        // First timeout in this level - one more chance
        setFeedback(`⏰ Dragon got Mario! The answer was ${currentQuestion.answer}. You have 1 more chance in this level!`)
        setTimeout(() => {
          setFeedback('')
          setDragonAttack(false)
          newQuestion(level)
        }, 2000)
      }
    }, 1000)
  }

  const checkAnswer = (answer) => {
    if (!currentQuestion || isAnswering) return

    setIsAnswering(true)
    setSelectedAnswer(answer)
    clearInterval(timerRef.current)

    const userNum = parseFloat(answer)
    const correctNum = parseFloat(currentQuestion.answer)
    const timeSaved = Math.max(0, timeLeft)

    if (Math.abs(userNum - correctNum) < 0.01) {
      // Calculate bonus: base points + time bonus
      const basePoints = level * 10
      const timeBonus = Math.floor(timeSaved * level * 0.5)
      const totalPoints = basePoints + timeBonus

      // Trigger shooting animation and dragon falling
      setIsShooting(true)
      setTimeout(() => {
        setDragonFalling(true)
        setIsShooting(false)
      }, 300)
      setTimeout(() => setDragonFalling(false), 1200)

      setFeedback(`🎉 Correct! Mario fired at the dragon! 💥 +${basePoints} pts + ${timeBonus} time bonus!`)
      setScore(score + totalPoints)
      setPlayerPosition(Math.min(playerPosition + 15, 85))

      setTimeout(() => {
        if (playerPosition + 15 >= 85) {
          setLevel(level + 1)
          setPlayerPosition(0)
          setWrongAnswersInLevel(0) // Reset wrong answers for new level
          setFeedback('🏁 Level Complete!')
          setTimeout(() => {
            setFeedback('')
            newQuestion(level + 1)
          }, 1500)
        } else {
          setFeedback('')
          newQuestion(level)
        }
      }, 1500)
    } else {
      const newWrongCount = wrongAnswersInLevel + 1
      setWrongAnswersInLevel(newWrongCount)

      if (newWrongCount >= 2) {
        // Second wrong answer in this level - game over
        setFeedback(`❌ Wrong! The answer was ${currentQuestion.answer}. You used your second chance - Game Over!`)
        setLives(lives - 1)
        setTimeout(() => setGameOver(true), 2000)
      } else {
        // First wrong answer in this level - one more chance
        setFeedback(`❌ Wrong! The answer was ${currentQuestion.answer}. You have 1 more chance in this level!`)
        setLives(lives - 1)
        setTimeout(() => {
          setFeedback('')
          newQuestion(level)
        }, 2000)
      }
    }
  }

  const resetGame = () => {
    setLevel(1)
    setScore(0)
    setLives(3)
    setPlayerPosition(0)
    setGameOver(false)
    setFeedback('')
    setSelectedAnswer(null)
    setDragonAttack(false)
    setWrongAnswersInLevel(0)
    setIsShooting(false)
    setDragonFalling(false)
    newQuestion(1)
  }

  // Calculate dragon position based on time remaining
  // Dragon comes from the RIGHT (opposite direction) and moves LEFT towards Mario
  const getDragonPosition = () => {
    const timeLimit = getTimeLimit(level)
    const timeProgress = 1 - (timeLeft / timeLimit)
    // Dragon starts from right (100%) and moves towards Mario's position (left)
    const dragonPos = 100 - (timeProgress * (100 - playerPosition))
    return Math.max(playerPosition, dragonPos)
  }

  // Timer color based on urgency
  const getTimerColor = () => {
    const limit = getTimeLimit(level)
    const percentage = (timeLeft / limit) * 100

    if (percentage > 60) return 'from-emerald-400 to-cyan-400'
    if (percentage > 30) return 'from-amber-400 to-orange-400'
    return 'from-red-400 to-rose-400'
  }

  if (gameOver) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-900 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 shadow-2xl shadow-red-500/25 text-center max-w-md">
          <div className="text-5xl mb-4">💀</div>
          <h1 className="text-3xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-orange-400 mb-3">
            Game Over!
          </h1>
          <p className="text-xl text-slate-300 mb-4">
            Final Score: <span className="text-amber-400 font-bold">{score}</span>
          </p>
          <p className="text-base text-slate-400 mb-6">
            You reached Level {level}
          </p>
          <button
            onClick={resetGame}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 text-white font-bold text-base transform hover:scale-105 hover:shadow-xl hover:shadow-emerald-500/25 transition-all duration-200 active:scale-95"
          >
            Try Again! 🔄
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4">
      {/* Header */}
      <div className="max-w-5xl mx-auto mb-4">
        <div className="grid grid-cols-4 gap-3">
          <div className="bg-white/10 backdrop-blur-xl rounded-xl px-4 py-2 border border-white/20">
            <div className="text-xs text-slate-400">LEVEL</div>
            <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400">
              {level}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl px-4 py-2 border border-white/20">
            <div className="text-xs text-slate-400">SCORE</div>
            <div className="text-2xl font-bold text-amber-400">
              {score}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl px-4 py-2 border border-white/20">
            <div className="text-xs text-slate-400">LIVES</div>
            <div className="text-2xl">
              {'❤️'.repeat(lives)}{'🖤'.repeat(3 - lives)}
            </div>
          </div>

          <div className="bg-white/10 backdrop-blur-xl rounded-xl px-4 py-2 border border-white/20">
            <div className="text-xs text-slate-400">TIME</div>
            <div className={`text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r ${getTimerColor()} ${timeLeft <= 5 ? 'animate-pulse' : ''}`}>
              {timeLeft}s
            </div>
          </div>
        </div>
      </div>

      {/* Game Area */}
      <div className="max-w-5xl mx-auto">
        {/* Mario's Path */}
        <div className="bg-white/5 backdrop-blur-xl rounded-2xl p-4 border border-white/10 shadow-2xl mb-4">
          <div className={`relative h-24 bg-gradient-to-r from-green-900/50 to-blue-900/50 rounded-xl border-2 border-white/10 overflow-hidden ${dragonAttack ? 'animate-pulse' : ''}`}>
            {/* Ground blocks */}
            <div className="absolute bottom-0 left-0 right-0 h-6 bg-gradient-to-b from-amber-700 to-amber-900 border-t-2 border-amber-600"></div>

            {/* Clouds */}
            <div className="absolute top-2 left-1/4 text-xl opacity-50">☁️</div>
            <div className="absolute top-3 right-1/3 text-lg opacity-40">☁️</div>

            {/* Dragon - coming from the RIGHT */}
            {!isAnswering && currentQuestion && !dragonFalling && (
              <>
                {/* Dragon fire breath effect - now shoots LEFT */}
                {timeLeft <= 5 && (
                  <div
                    className="absolute bottom-6 text-2xl animate-pulse"
                    style={{ left: `${getDragonPosition() - 8}%` }}
                  >
                    🔥
                  </div>
                )}
                {/* Dragon - facing left (coming from right) */}
                <div
                  className={`absolute bottom-6 text-4xl transform transition-all duration-1000 ease-linear scale-x-[-1] ${
                    timeLeft <= 10 ? 'animate-bounce' : ''
                  }`}
                  style={{ left: `${getDragonPosition()}%` }}
                >
                  🐉
                </div>
              </>
            )}

            {/* Falling Dragon Animation */}
            {dragonFalling && (
              <div
                className="absolute text-4xl animate-dragon-fall scale-x-[-1]"
                style={{ left: `${getDragonPosition()}%`, bottom: '1.5rem' }}
              >
                🐉
              </div>
            )}

            {/* Fireball when shooting */}
            {isShooting && (
              <div
                className="absolute bottom-8 text-2xl animate-fireball"
                style={{ left: `${playerPosition + 5}%` }}
              >
                🔥
              </div>
            )}

            {/* Dragon attack animation */}
            {dragonAttack && (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-8xl animate-ping">🔥</div>
                <div className="absolute text-7xl">💥</div>
              </div>
            )}

            {/* Finish flag */}
            <div className="absolute right-3 bottom-6 text-3xl transform hover:scale-110 transition-transform">
              🏁
            </div>

            {/* Mario */}
            <div
              className={`absolute bottom-6 text-4xl transform transition-all duration-500 ease-out ${
                dragonAttack ? 'opacity-30 scale-50' : ''
              } ${
                isShooting ? 'scale-110' : ''
              }`}
              style={{ left: `${playerPosition}%` }}
            >
              🍄
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-3 bg-white/10 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 transition-all duration-500 ease-out"
              style={{ width: `${playerPosition}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-xl rounded-2xl p-6 border border-white/20 shadow-2xl shadow-purple-500/20">
          <h2 className="text-lg font-light text-slate-300 tracking-wide mb-4 text-center">
            Solve to help Mario advance!
          </h2>

          {currentQuestion && (
            <div className="text-center mb-4">
              <div className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-violet-400 via-fuchsia-400 to-pink-400 mb-6 tracking-tight">
                {currentQuestion.question} = ?
              </div>

              {/* Multiple Choice Options */}
              <div className="grid grid-cols-2 gap-3 max-w-2xl mx-auto">
                {options.map((option, index) => {
                  const isCorrect = option.toString() === currentQuestion.answer
                  const isSelected = selectedAnswer === option.toString()

                  let buttonClass = "px-6 py-4 rounded-xl text-xl font-bold transform transition-all duration-200 "

                  if (isAnswering) {
                    if (isSelected && isCorrect) {
                      buttonClass += "bg-gradient-to-r from-emerald-500 to-green-500 text-white scale-105 ring-4 ring-emerald-400/50"
                    } else if (isSelected && !isCorrect) {
                      buttonClass += "bg-gradient-to-r from-red-500 to-rose-500 text-white scale-95 ring-4 ring-red-400/50"
                    } else if (isCorrect) {
                      buttonClass += "bg-gradient-to-r from-emerald-500 to-green-500 text-white ring-4 ring-emerald-400/50"
                    } else {
                      buttonClass += "bg-white/5 text-slate-500 border border-white/10"
                    }
                  } else {
                    buttonClass += "bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 hover:from-violet-500 hover:to-fuchsia-500 text-white border-2 border-violet-400/50 hover:border-violet-300 hover:scale-105 hover:shadow-xl hover:shadow-violet-500/30 active:scale-95"
                  }

                  return (
                    <button
                      key={index}
                      onClick={() => checkAnswer(option.toString())}
                      disabled={isAnswering}
                      className={buttonClass}
                    >
                      {option}
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {/* Feedback */}
          {feedback && (
            <div className={`mt-4 p-4 rounded-xl text-center text-base font-medium border-2 transform transition-all duration-300 ${
              feedback.includes('Correct') || feedback.includes('Complete')
                ? 'bg-emerald-500/20 border-emerald-400 text-emerald-300'
                : 'bg-red-500/20 border-red-400 text-red-300'
            }`}>
              {feedback}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-4 bg-white/5 backdrop-blur-xl rounded-xl p-4 border border-white/10">
          <h3 className="text-base font-bold text-slate-300 mb-2">📚 How to Play:</h3>
          <ul className="text-slate-400 text-sm space-y-1">
            <li>• 🐉 <span className="text-red-400 font-semibold">Dragon from RIGHT!</span> Answer to fire! 🔥 💥</li>
            <li>• <span className="text-amber-400 font-semibold">1 wrong answer allowed per level</span> - 2nd mistake = game over! ⚠️</li>
            <li>• Time gets harder each level: 30s → 27s → 24s... (min 10s) ⏰</li>
            <li>• Faster answers = more points! ⚡ Get 5 right to level up! 🏁</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default App
