from flask import Flask, abort, jsonify, render_template, request

from database import Database
from methods import ALL_METHODS, find_method
from methods.base import CalculationError


def create_app(database_path="numerical.db"):
    app = Flask(__name__)
    database = Database(database_path)

    # Pages

    @app.route("/")
    def home():
        return render_template("home.html", methods=ALL_METHODS)

    @app.route("/methods/<slug>")
    def method_page(slug):
        method = find_method(slug)
        if method is None:
            abort(404)
        return render_template("method.html", method=method)

    # API

    @app.route("/api/methods")
    def list_methods():
        return jsonify([method.info() for method in ALL_METHODS])

    @app.route("/api/methods/<slug>/calculate", methods=["POST"])
    def calculate(slug):
        method = find_method(slug)
        if method is None:
            return jsonify(error="Topic not found."), 404

        inputs = request.get_json(silent=True)
        if not isinstance(inputs, dict):
            return jsonify(error="The request body must be a JSON object."), 400

        try:
            result = method.solve(inputs)
        except CalculationError as error:
            return jsonify(error=str(error)), 400

        new_id = database.save(slug, inputs, result)
        return jsonify(id=new_id, result=result), 201

    @app.route("/api/calculations")
    def list_calculations():
        limit = request.args.get("limit", 20, type=int)
        if limit < 1 or limit > 100:
            return jsonify(error="limit must be from 1 to 100."), 400
        return jsonify(database.get_all(request.args.get("method"), limit))

    @app.route("/api/calculations/<int:calculation_id>")
    def get_calculation(calculation_id):
        calculation = database.get_one(calculation_id)
        if calculation is None:
            return jsonify(error="Calculation not found."), 404
        return jsonify(calculation)

    @app.route("/api/calculations/<int:calculation_id>", methods=["DELETE"])
    def delete_calculation(calculation_id):
        if not database.delete(calculation_id):
            return jsonify(error="Calculation not found."), 404
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(port=5000)
