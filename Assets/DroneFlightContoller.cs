using UnityEngine;

public class DroneFlightContoller : MonoBehaviour
{

    public string fileName = "File Name";
    public int number = 0;

    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        string path = Application.dataPath + "/example.txt";

        if (File.Exists(path))
        {
            string contents = File.ReadAllText(path);
            Debug.Log("File contents:\n" + contents);
        }
        else
        {
            Debug.LogWarning("File not found at " + path);
        }


        this.transform.position = Vector3.zero;
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
