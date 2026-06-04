import CalibrationSession from '../../pages/CalibrationSession'

export default function CalibrationStep({ onComplete, onSkip }) {
  return <CalibrationSession onComplete={onComplete} onSkip={onSkip} />
}
