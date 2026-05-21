from he_cr_model.reactions import enabled_reactions
from he_cr_model.solver import apply_enabled_ai_losses


def test_ai_loss_decreases_target_population() -> None:
    seed = {"3_1S": 1.0e10, "3_3S": 1.0e10}
    result = apply_enabled_ai_losses(
        seed_populations=seed,
        reactions=enabled_reactions(),
        neutral_density_cm3=2.45e19,
        timescale_s=1.0e-9,
    )
    assert result.populations["3_1S"] < seed["3_1S"]
    assert result.populations["3_3S"] < seed["3_3S"]
    assert all(value >= 0 for value in result.populations.values())
