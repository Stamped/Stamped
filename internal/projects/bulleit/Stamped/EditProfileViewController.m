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
static NSString* const kUpdateStampPath = @"/account/customize_stamp.json";

@implementation EditProfileViewController

@synthesize user = user_;
@synthesize stampImageView = stampImageView_;
@synthesize userImageView = userImageView_;

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
  self.userImageView.imageURL = user_.profileImageURL;
  // Do any additional setup after loading the view from its nib.
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.stampImageView = nil;
  self.userImageView = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  // Return YES for supported orientations
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - Actions

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)editStampButtonPressed:(id)sender {
  StampCustomizerViewController* vc = [[StampCustomizerViewController alloc] initWithNibName:@"StampCustomizerViewController" bundle:nil];
  vc.delegate = self;
  [self.navigationController presentModalViewController:vc animated:YES];
  [vc release];
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
    UIImage* newPhoto = UIGraphicsGetImageFromCurrentImageContext();
    UIGraphicsEndImageContext();
    userImageView_.image = newPhoto;
  }
  
  [self dismissModalViewControllerAnimated:YES];
}

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)picker {
  [self dismissModalViewControllerAnimated:YES];
}


@end
