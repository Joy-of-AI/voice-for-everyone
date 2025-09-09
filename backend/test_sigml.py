from services.sigml_synthesis import sigml_synthesis

def test_sigml():
    # Test text to HamNoSys conversion
    text = "hello world"
    hamnosys = sigml_synthesis.text_to_hamnosys(text)
    print(f"Text: {text}")
    print(f"HamNoSys: {hamnosys}")
    
    # Test HamNoSys to SiGML conversion
    sigml = sigml_synthesis.hamnosys_to_sigml(hamnosys)
    print(f"SiGML: {sigml[:200]}...")
    
    # Test complete sign animation generation
    animation = sigml_synthesis.generate_sign_animation("hello", 3.0)
    print(f"Animation duration: {animation['duration']}s")
    print(f"Total frames: {animation['total_frames']}")
    print(f"Keyframes: {len(animation['keyframes'])}")
    
    # Test JASigning export
    jasigning = sigml_synthesis.export_to_jasigning(animation)
    print(f"JASigning keyframes: {len(jasigning['animation']['keyframes'])}")
    
    # Test dictionary stats
    stats = sigml_synthesis.get_dictionary_stats()
    print(f"Dictionary stats: {stats}")
    
    # Test custom sign addition
    success = sigml_synthesis.add_custom_sign("test", "A@chest~A@forward")
    print(f"Added custom sign: {success}")
    
    # Test SiGML validation
    is_valid = sigml_synthesis.validate_sigml(sigml)
    print(f"SiGML validation: {is_valid}")

if __name__ == "__main__":
    test_sigml()
