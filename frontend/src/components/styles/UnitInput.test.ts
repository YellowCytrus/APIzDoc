import { mount } from '@vue/test-utils';
import { describe, expect, it } from 'vitest';
import UnitInput from './UnitInput.vue';

describe('UnitInput', () => {
  it('renders mm value in selected unit and emits mm on input', async () => {
    const wrapper = mount(UnitInput, {
      props: {
        valueMm: 25.4,
        unit: 'in',
        allowedUnits: ['mm', 'cm', 'in'],
      },
    });
    const numberInput = wrapper.get('input[type="number"]');
    expect(Number((numberInput.element as HTMLInputElement).value)).toBeCloseTo(1, 12);

    await numberInput.setValue('2');
    await numberInput.trigger('change');
    const events = wrapper.emitted('commit');
    expect(events).toBeTruthy();
    expect(events?.[events.length - 1]?.[0]).toBeCloseTo(50.8, 12);
  });

  it('shows context error and blocks em conversion without context', async () => {
    const wrapper = mount(UnitInput, {
      props: {
        valueMm: 10,
        unit: 'em',
        allowedUnits: ['mm', 'cm', 'in', 'em'],
      },
    });
    expect(wrapper.text()).toContain('Для единицы em нужен корректный размер шрифта.');
    await wrapper.get('input[type="number"]').setValue('3');
    await wrapper.get('input[type="number"]').trigger('change');
    expect(wrapper.emitted('commit')).toBeFalsy();
  });
});
