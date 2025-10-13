import { useState } from "react";
import axiosClient from "../../api/axiosClient";

export default function QuotationForm() {
  const [form, setForm] = useState({
    customer_name: "",
    customer_email: "",
    currency: "MXN",
    date: new Date().toISOString().split("T")[0],
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const validate = () => {
    const newErrors = {};
    if (!form.customer_name) newErrors.customer_name = "El nombre es obligatorio";
    if (!form.customer_email) newErrors.customer_email = "El correo es obligatorio";
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    try {
      const res = await axiosClient.post("/quotations/", form);
      alert("✅ Cotización creada con éxito");
      console.log(res.data);
    } catch (err) {
      alert("❌ Error al crear la cotización");
    }
  };

  return (
    <div className="quotation-form">
      <h2>🧾 Crear nueva cotización</h2>
      <form onSubmit={handleSubmit}>
        <label>
          Cliente:
          <input
            name="customer_name"
            value={form.customer_name}
            onChange={handleChange}
          />
          {errors.customer_name && <p className="error">{errors.customer_name}</p>}
        </label>

        <label>
          Correo del cliente:
          <input
            name="customer_email"
            type="email"
            value={form.customer_email}
            onChange={handleChange}
          />
          {errors.customer_email && <p className="error">{errors.customer_email}</p>}
        </label>

        <label>
          Moneda:
          <select name="currency" value={form.currency} onChange={handleChange}>
            <option value="MXN">MXN (Peso Mexicano)</option>
            <option value="USD">USD (Dólar)</option>
          </select>
        </label>

        <button type="submit">Guardar Cotización</button>
      </form>
    </div>
  );
}
