import { nombreEscenario } from '../lib/red';
import type { Escenario } from '../types/red';

export function SelectorEscenario({ valor, onChange }: { valor: Escenario; onChange: (valor: Escenario) => void }) {
  return <fieldset className="selector-escenario">
    <legend>Aumento de la tasa de crecimiento poblacional</legend>
    <div className="selector-opciones">
      {([1, 1.1, 1.3] as const).map(escenario => <button key={escenario} type="button" aria-pressed={valor === escenario} aria-label={`Escenario ${nombreEscenario(escenario)}`} onClick={() => onChange(escenario)}>
        {nombreEscenario(escenario)}
      </button>)}
    </div>
  </fieldset>;
}
