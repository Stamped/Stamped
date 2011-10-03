//
//  EditProfileViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/3/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "EditProfileViewController.h"

#import <MobileCoreServices/UTCoreTypes.h>
#import <RestKit/RestKit.h>

#import "AccountManager.h"
#import "User.h"
#import "Util.h"
#import "STImageView.h"

static const CGFloat kProfileImageSize = 500;
static const NSUInteger kMaxNameLength = 80;
static const NSUInteger kMaxLocationLength = 80;
static const NSUInteger kMaxBioLength = 200;
static NSString* const kUpdateStampPath = @"/account/customize_stamp.json";
static NSString* const kUpdateProfilePath = @"/account/update_profile.json";
static NSString* const kUpdateProfileImagePath = @"/account/update_profile_image.json";
static const NSUInteger kMaxPicUploadTries = 3;

@interface EditProfileViewController ()
@property (nonatomic, readonly) UIResponder* firstResponder;
@property (nonatomic, retain) UIImage* newProfilePic;
@property (nonatomic, assign) NSUInteger numPicUploadTries;
@end

@implementation EditProfileViewController

@synthesize user = user_;
@synthesize stampImageView = stampImageView_;
@synthesize userImageView = userImageView_;
@synthesize nameTextField = nameTextField_;
@synthesize locationTextField = locationTextField_;
@synthesize aboutTextField = aboutTextField_;
@synthesize containerView = containerView_;
@synthesize saveButton = saveButton_;
@synthesize saveIndicator = saveIndicator_;
@synthesize firstResponder = firstResponder_;
@synthesize profileImageIndicator = profileImageIndicator_;
@synthesize newProfilePic = newProfilePic_;
@synthesize numPicUploadTries = numPicUploadTries_;

- (id)init {
  self = [self initWithNibName:@"EditProfileViewController" bundle:nil];
  if (self) {
  }
  return self;
}

- (void)dealloc {
  self.user = nil;
  self.stampImageView = nil;
  self.userImageView = nil;
  self.nameTextField = nil;
  self.locationTextField = nil;
  self.aboutTextField = nil;
  self.containerView = nil;
  self.saveIndicator = nil;
  self.saveButton = nil;
  self.profileImageIndicator = nil;
  self.newProfilePic = nil;
  firstResponder_ = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  self.stampImageView.image = user_.stampImage;
  self.userImageView.userInteractionEnabled = NO;
  self.userImageView.layer.shadowOpacity = 0;
  self.userImageView.imageURL = user_.profileImageURL;
  self.nameTextField.text = user_.name;
  self.locationTextField.text = user_.location;
  self.aboutTextField.text = user_.bio;
  saveButton_.enabled = NO;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.stampImageView = nil;
  self.userImageView = nil;
  self.nameTextField = nil;
  self.locationTextField = nil;
  self.aboutTextField = nil;
  self.containerView = nil;
  self.saveIndicator = nil;
  self.saveButton = nil;
  self.profileImageIndicator = nil;
  firstResponder_ = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Actions

- (IBAction)saveButtonPressed:(id)sender {
  if (!nameTextField_.text.length) {
    UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp" 
                                                     message:@"Your name is required."
                                                    delegate:nil
                                           cancelButtonTitle:nil
                                           otherButtonTitles:@"Yay!", nil] autorelease];
    [alert show];
    return;
  }
  [saveIndicator_ startAnimating];
  saveButton_.enabled = NO;
  [saveButton_ setTitle:nil forState:UIControlStateNormal];

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUpdateProfilePath 
                                                                    delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = mapping;
  NSMutableDictionary* params = [NSMutableDictionary dictionaryWithObject:nameTextField_.text forKey:@"name"];
  if (locationTextField_.text.length > 0)
    [params setObject:locationTextField_.text forKey:@"location"];
  if (aboutTextField_.text.length > 0)
    [params setObject:aboutTextField_.text forKey:@"bio"];
  objectLoader.params = params;
  [objectLoader send];
  
  [firstResponder_ resignFirstResponder];
}

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)editStampButtonPressed:(id)sender {
  StampCustomizerViewController* vc = [[StampCustomizerViewController alloc] initWithNibName:@"StampCustomizerViewController" bundle:nil];
  vc.delegate = self;
  [self.navigationController presentModalViewController:vc animated:YES];
  [vc release];
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObject:(id)object {
  NSLog(@"Success: %@", objectLoader.response.bodyAsString);
  if ([objectLoader.resourcePath isEqualToString:kUpdateProfilePath]) {
    [saveIndicator_ stopAnimating];
    saveButton_.enabled = YES;
    [saveButton_ setTitle:@"Saved!" forState:UIControlStateNormal];
  } else if ([objectLoader.resourcePath isEqualToString:kUpdateProfileImagePath]) {
    [profileImageIndicator_ stopAnimating];
    userImageView_.image = self.newProfilePic;
    userImageView_.hidden = NO;
  }
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  NSLog(@"Error: %@", objectLoader.response.bodyAsString);
  if ([objectLoader.resourcePath isEqualToString:kUpdateProfilePath]) {
    [saveIndicator_ stopAnimating];
    saveButton_.enabled = YES;
    [saveButton_ setTitle:@"Save" forState:UIControlStateNormal];
  } else if ([objectLoader.resourcePath isEqualToString:kUpdateProfileImagePath]) {
    [profileImageIndicator_ stopAnimating];
    userImageView_.hidden = NO;
  }
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp" 
                                                   message:@"There was a problem. Try again please."
                                                  delegate:nil
                                         cancelButtonTitle:nil
                                         otherButtonTitles:@"OK", nil] autorelease];
  [alert show];
  return;
}

#pragma mark - UITextFieldDelegate methods.

- (BOOL)textField:(UITextField*)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString*)string {
  NSString* text = [textField.text stringByReplacingCharactersInRange:range withString:string];
  if (textField == nameTextField_) {
    return text.length <= kMaxNameLength;
  } else if (textField == aboutTextField_) {
    return text.length <= kMaxBioLength;
  } else if (textField == locationTextField_) {
    return text.length <= kMaxLocationLength;
  }

  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  saveButton_.enabled = YES;
  [saveButton_ setTitle:@"Save" forState:UIControlStateNormal];
  firstResponder_ = textField;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     containerView_.frame = CGRectOffset(containerView_.frame, 0, -95);
                   }
                   completion:nil];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  saveButton_.enabled = NO;
  firstResponder_ = nil;
  [UIView animateWithDuration:0.3
                        delay:0
                      options:UIViewAnimationOptionBeginFromCurrentState
                   animations:^{
                     containerView_.frame = CGRectOffset(containerView_.frame, 0, 95);
                   }
                   completion:nil];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

#pragma mark - StampCustomizerViewControllerDelegate methods.

- (void)stampCustomizer:(StampCustomizerViewController*)customizer
      chosePrimaryColor:(NSString*)primary
         secondaryColor:(NSString*)secondary {
  User* user = [AccountManager sharedManager].currentUser;
  user.primaryColor = primary;
  user.secondaryColor = secondary;
  self.stampImageView.image = user.stampImage;
  [[NSNotificationCenter defaultCenter] postNotificationName:kCurrentUserHasUpdatedNotification
                                                      object:[AccountManager sharedManager]];

  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* mapping = [objectManager.mappingProvider mappingForKeyPath:@"User"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:kUpdateStampPath 
                                                                    delegate:nil];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = mapping;
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:primary, @"color_primary",
                                                                   secondary, @"color_secondary", nil];
  [objectLoader send];
}

- (IBAction)changePhotoButtonPressed:(id)sender {
  UIActionSheet* sheet = [[UIActionSheet alloc] initWithTitle:nil
                                                     delegate:self
                                            cancelButtonTitle:@"Cancel"
                                       destructiveButtonTitle:nil
                                            otherButtonTitles:@"Take photo", @"Choose photo", nil];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
  [sheet release];
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 2)
    return;  // Canceled.
  
  UIImagePickerController* imagePicker = [[UIImagePickerController alloc] init];
  imagePicker.modalTransitionStyle = UIModalTransitionStyleCrossDissolve;
  imagePicker.delegate = self;
  imagePicker.allowsEditing = YES;
  imagePicker.mediaTypes = [NSArray arrayWithObject:(NSString*)kUTTypeImage];
  
  if (buttonIndex == 0) {
    imagePicker.sourceType = UIImagePickerControllerSourceTypeCamera;
    imagePicker.cameraDevice = UIImagePickerControllerCameraDeviceFront;
  }
  [self presentModalViewController:imagePicker animated:YES];
  [imagePicker release];
}

#pragma mark - UIImagePickerControllerDelegate methods.

- (void)imagePickerController:(UIImagePickerController*)picker didFinishPickingMediaWithInfo:(NSDictionary*)info {
  [self view];
  NSString* mediaType = [info objectForKey:UIImagePickerControllerMediaType];
  
  if (CFStringCompare((CFStringRef)mediaType, kUTTypeImage, 0) == kCFCompareEqualTo) {
    UIImage* photo = (UIImage*)[info objectForKey:UIImagePickerControllerEditedImage];
    
    UIGraphicsBeginImageContext(CGSizeMake(kProfileImageSize, kProfileImageSize));
    [photo drawInRect:CGRectMake(0, 0, kProfileImageSize, kProfileImageSize)];
    self.newProfilePic = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    userImageView_.hidden = YES;
    [profileImageIndicator_ startAnimating];
    numPicUploadTries_ = 0;
    RKObjectManager* manager = [RKObjectManager sharedManager];
    RKObjectMapping* mapping = [manager.mappingProvider mappingForKeyPath:@"User"];
    RKObjectLoader* loader = [manager objectLoaderWithResourcePath:kUpdateProfileImagePath
                                                          delegate:self];
    loader.method = RKRequestMethodPOST;
    loader.objectMapping = mapping;
    if (!self.newProfilePic)
      return;
    
    RKParams* params = [RKParams params];
    NSData* imageData = UIImageJPEGRepresentation(self.newProfilePic, 0.8);
    [params setData:imageData MIMEType:@"image/jpeg" forParam:@"profile_image"];
    loader.params = params;
    [loader send];
  }
  
  [self dismissModalViewControllerAnimated:YES];
}

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)picker {
  [self dismissModalViewControllerAnimated:YES];
}


@end
