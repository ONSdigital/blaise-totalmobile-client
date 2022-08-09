from models.totalmobile_world_model import TotalmobileWorldModel, World


def test_import_worlds_returns_a_populated_model():
    worlds = [
    {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "identity": {
            "reference": "Region 1"
        },
        "type": "foo"
    },
    {
        "id": "8fa85f64-5717-4562-b3fc-2c963f66afa7",
        "identity": {
            "reference": "Region 2"
        },
        "type": "foo"
    },
]
    result = TotalmobileWorldModel.import_worlds(worlds)

    assert result.worlds[0].region == "Region 1"
    assert result.worlds[0].id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"

    assert result.worlds[1].region == "Region 2"
    assert result.worlds[1].id == "8fa85f64-5717-4562-b3fc-2c963f66afa7"


def test_get_world_id_returns_the_correct_id_for_region():
    totalmobile_world_model = TotalmobileWorldModel(
        worlds=[World(region="Region 1", id="3fa85f64-5717-4562-b3fc-2c963f66afa6"),
                   World(region="Region 2", id="8fa85f64-5717-4562-b3fc-2c963f66afa7")]
    )

    result = totalmobile_world_model.get_world_id("Region 1")

    assert result == "3fa85f64-5717-4562-b3fc-2c963f66afa6"