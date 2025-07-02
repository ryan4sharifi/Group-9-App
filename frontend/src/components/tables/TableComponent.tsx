// src/components/tables/TableComponent.tsx
import React from "react";
import { DataGrid, GridColDef } from "@mui/x-data-grid";

interface TableProps {
  rows: any[];
  columns: GridColDef[];
}

const TableComponent: React.FC<TableProps> = ({ rows, columns }) => {
  return (
    <div style={{ height: 400, width: "100%" }}>
      <DataGrid
        rows={rows}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: { pageSize: 5, page: 0 },
          },
        }}
        pageSizeOptions={[5]}
        disableRowSelectionOnClick
      />
    </div>
  );
};

export default TableComponent;