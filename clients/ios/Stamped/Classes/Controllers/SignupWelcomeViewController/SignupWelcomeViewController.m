//
//  SignupWelcomeViewController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "SignupWelcomeViewController.h"
#import "StampColorPickerView.h"
#import "SocialSignupHeaderView.h"
#import "STTextFieldTableCell.h"
#import "StampCustomizeViewController.h"
#import "STTwitter.h"
#import "STAuth.h"
#import "STFacebook.h"
#import "STAvatarView.h"
#import "FindFriendsViewController.h"
#import "SignupCameraTableCell.h"
#import "STAccountParameters.h"
#import "LoginLoadingView.h"
#import "STS3Uploader.h"
#import "STInboxViewController.h"
#import "STMenuController.h"
#import "STEvents.h"
#import "STBlockUIView.h"
#import "QuartzUtils.h"
#import "STNavigationItem.h"
#import "STStampedAPI.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STRootViewController.h"
#import "STImageCache.h"

@interface SignupWelcomeViewController ()
@property(nonatomic,readonly) SignupWelcomeType signupType;
@property(nonatomic,retain) STS3Uploader *avatarUploader;
@property(nonatomic,retain) NSString *avatarTempPath;
@property (nonatomic, readwrite, retain) UIImage* avatarImage;
@end

@implementation SignupWelcomeViewController
@synthesize signupType=_signupType;
@synthesize userInfo;
@synthesize avatarUploader;
@synthesize avatarTempPath;
@synthesize avatarImage = _avatarImage;

- (id)initWithType:(SignupWelcomeType)type {
    if ((self = [super initWithStyle:UITableViewStyleGrouped])) {
        //self.title = NSLocalizedString(@"Welcome", @"Welcome");
        _signupType = type;
        [STEvents addObserver:self selector:@selector(signupFinished:) event:EventTypeSignupFinished];
        [STEvents addObserver:self selector:@selector(signupFailed:) event:EventTypeSignupFailed];
        self.navigationItem.hidesBackButton = YES;
        self.avatarUploader = [[[STS3Uploader alloc] init] autorelease];
    }
    return self;
}

- (void)dealloc {
    [self.avatarUploader cancel];
    self.avatarUploader = nil;
    [STEvents removeObserver:self];
    [_avatarImage release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    self.tableView.showsVerticalScrollIndicator = NO;
    self.tableView.separatorStyle = UITableViewCellSeparatorStyleNone;
    self.tableView.allowsSelection = NO;
    
    if (!self.tableView.tableHeaderView) {
        
        SocialSignupHeaderView *header = [[SocialSignupHeaderView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 104.0f)];
        header.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        header.backgroundColor = [UIColor clearColor];
        self.tableView.tableHeaderView = header;
        
        UIColor *color1 =  [UIColor colorWithRed:0.0f green:0.290f blue:0.698f alpha:1.0f];
        UIColor *color2 =  [UIColor colorWithRed:0.0f green:0.3411f blue:0.819f alpha:1.000];
        NSArray *colors = [[NSArray alloc] initWithObjects:color1, color2, nil];
        [header.stampView setupWithColors:colors];
        [colors release];
        
        if (_signupType == SignupWelcomeTypeTwitter) {
            
            NSDictionary *userDic = [[STTwitter sharedInstance] twitterUser];
            if (userDic) {
                NSString *location = [userDic objectForKey:@"location"];
                if (location != nil && ![location isEqual:[NSNull null]]) {
                    header.subTitleLabel.text = location;
                }
                NSString *description = [userDic objectForKey:@"description"];
                if (description != nil && ![location isEqual:[NSNull null]]) {
                    header.detailLabel.text = description;
                }
                
                header.titleLabel.text = [userDic objectForKey:@"name"];
                NSString *avatar = [[userDic objectForKey:@"profile_image_url"] stringByReplacingOccurrencesOfString:@"photo_normal.jpg" withString:@"photo_bigger.jpg"] ;
                [header.imageView setImageURL:[NSURL URLWithString:avatar]];
                [self prepareAvatarImageWithPath:avatar];
                [header setNeedsLayout];
            }

        } else if (_signupType == SignupWelcomeTypeFacebook) {
            
            NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
            header.titleLabel.text = [dictionary objectForKey:@"name"];
            [header setNeedsLayout];
            
            NSString *avatar = [NSString stringWithFormat:@"https://graph.facebook.com/%@/picture&type=large", [dictionary objectForKey:@"id"]];
            [self prepareAvatarImageWithPath:avatar];
            [header.imageView setImageURL:[NSURL URLWithString:avatar]];
            [header setNeedsLayout];

        } else if (_signupType == SignupWelcomeTypeEmail) {
            
            if (self.userInfo) {
                
                if (self.userInfo.name) {
                    header.titleLabel.text = self.userInfo.name;
                }
                if (self.userInfo.screenName) {
                    header.detailLabel.text = [NSString stringWithFormat:@"@%@", self.userInfo.screenName];
                }

            }
            
        }
        [header release];

    }
    
    if (!self.tableView.tableFooterView) {
        StampColorPickerView *view = [[StampColorPickerView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 220.0f)];
        view.backgroundColor = [UIColor clearColor];
        view.delegate = (id<StampColorPickerDelegate>)self;
        view.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        self.tableView.tableFooterView = view;
        [view release];
    }
    
    if (!self.tableView.backgroundView) {
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.tableView.bounds];
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
        }];
        self.tableView.backgroundView = background;
        [background release];
    }
    
    if (!self.navigationItem.rightBarButtonItem) {
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Next", @"Next") style:UIBarButtonItemStyleBordered target:self action:@selector(next:)];
        self.navigationItem.rightBarButtonItem = item;
        [item release];
    }
    
    if (!self.navigationItem.leftBarButtonItem && _signupType != SignupWelcomeTypeEmail) {
        STNavigationItem *item = [[STNavigationItem alloc] initWithTitle:NSLocalizedString(@"Cancel", @"Cancel") style:UIBarButtonItemStyleBordered target:self action:@selector(cancel:)];
        self.navigationItem.leftBarButtonItem = item;
        [item release];
    }
    
    
}

- (void)prepareAvatarImageWithPath:(NSString*)path {
    [[STImageCache sharedInstance] imageForImageURL:path andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
        if (image && !self.avatarImage) {
            self.avatarImage = image;
        }
    }];
}

- (void)viewDidUnload {
    self.tableView.tableHeaderView=nil;
    self.tableView=nil;
    [super viewDidUnload];
}

- (void)viewDidAppear:(BOOL)animated {
    [super viewDidAppear:animated];
    [Util setTitle:@"Welcome" forController:self];
}

- (void)viewWillDisappear:(BOOL)animated {
    [super viewWillDisappear:animated];
    [Util setTitle:nil forController:self];
}
//
//- (void)viewDidAppear:(BOOL)animated {
//    [super viewDidAppear:animated];
//    if (self.signupType ==SignupWelcomeTypeFacebook) {
//        [[STFacebook sharedInstance] showFacebookAlert];
//    }
//}

#pragma mark - Setters

- (void)setLoading:(BOOL)loading {
    
    if (loading) {
        
        if (!_loadingView) {
            
            STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.view.bounds];
            background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
            [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
                drawGradient([UIColor colorWithRed:0.961f green:0.961f blue:0.957f alpha:1.0f].CGColor, [UIColor colorWithRed:0.898f green:0.898f blue:0.898f alpha:1.0f].CGColor, ctx);
            }];
            [self.view addSubview:background];
            _loadingView = background;
            [background release];
            _loadingView.layer.zPosition = 100;
            _loadingView.alpha = 0.0f;
            
            STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            LoginLoadingView *view = [[LoginLoadingView alloc] initWithFrame:CGRectMake(0.0f, (_loadingView.bounds.size.height-60.0f)/2, _loadingView.bounds.size.width, 60.0f)];
            view.titleLabel.text = (_signupType == SignupWelcomeTypeEmail) ? @"Saving..." : cell.textField.text;
            [_loadingView addSubview:view];
            [view release];
            
            [UIView animateWithDuration:0.2f animations:^{
                _loadingView.alpha = 1.0f;
            }];
            
        }
        
    } else {
        
        if (_loadingView) {
            
            UIView *view = _loadingView;
            _loadingView = nil;
            [UIView animateWithDuration:0.2f animations:^{
                view.alpha = 1.0f;
            } completion:^(BOOL finished) {
                [view removeFromSuperview];
            }];
            
        }
        
    }
    
}


#pragma mark - Notifications

- (void)signupFinished:(NSNotification*)notification {
    if (self.avatarImage) {
        [STStampedAPI sharedInstance].currentUserImage = self.avatarImage;
    }
    FindFriendsViewController *controller = [[FindFriendsViewController alloc] init];
    controller.navigationItem.hidesBackButton = YES;
    [self.navigationController pushViewController:controller animated:YES];
    [controller release];
    SignupWelcomeType signupType = self.signupType;
    [Util executeWithDelay:1 onMainThread:^{
        if ([Util topController] == controller && signupType == SignupWelcomeTypeFacebook) {
            [[STFacebook sharedInstance] showFacebookAlert];
        }
    }];
        
}

- (void)signupFailed:(NSNotification*)notification {
    [Util warnWithAPIError:notification.object andBlock:nil];
    [self setLoading:NO];
}


#pragma mark - Actions

- (void)next:(id)sender {
    
    [self.tableView endEditing:YES];
    [self.tableView setContentOffset:CGPointZero animated:YES];
    [self setLoading:YES];

    StampColorPickerView *view = (StampColorPickerView*)self.tableView.tableFooterView;
    NSArray *colors = [view colors];
    UIColor *color = [colors objectAtIndex:0];
    NSString *primaryColor = [color hexString];
    color = [colors objectAtIndex:1];
    NSString *secondaryColor = [color hexString];

    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];

    if (_signupType == SignupWelcomeTypeTwitter) {
        
        STAccountParameters *parameters = [[STAccountParameters alloc] init];
        parameters.screenName = cell.textField.text;
        parameters.primaryColor = primaryColor;
        parameters.secondaryColor = secondaryColor;

        NSDictionary *userDic = [[STTwitter sharedInstance] twitterUser];
        
        NSString *name = [userDic objectForKey:@"name"];
        if (name != nil && ![name isEqual:[NSNull null]]) {
            parameters.name = name;
        } else {
            parameters.name = parameters.screenName;
        }
        
        NSString *location = [userDic objectForKey:@"location"];
        if (location != nil && ![location isEqual:[NSNull null]]) {
            parameters.location = location;
        }
        
        NSString *description = [userDic objectForKey:@"description"];
        if (description != nil && ![description isEqual:[NSNull null]]) {
            parameters.bio = description;
        }
        
        NSString *link = [userDic objectForKey:@"url"];
        if (link != nil && ![link isEqual:[NSNull null]]) {
            parameters.website = link;
        }
        
        NSString *avatar = [[userDic objectForKey:@"profile_image_url"] stringByReplacingOccurrencesOfString:@"photo_normal.jpg" withString:@"photo_bigger.jpg"] ;
        parameters.tempImageURL = avatar;
        [[STAuth sharedInstance] twitterSignupWithToken:[[STTwitter sharedInstance] twitterToken] secretToken:[[STTwitter sharedInstance] twitterTokenSecret] params:parameters];
        [parameters release];

    } else if (_signupType == SignupWelcomeTypeFacebook) {
        
        STAccountParameters *parameters = [[STAccountParameters alloc] init];
        parameters.screenName = cell.textField.text;
        parameters.primaryColor = primaryColor;
        parameters.secondaryColor = secondaryColor;

        NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
        
        NSString *name = [dictionary objectForKey:@"name"];
        if (name != nil && ![name isEqual:[NSNull null]]) {
            parameters.name = name;
        } else {
            parameters.name = parameters.screenName;
        }

        NSString *email = [dictionary objectForKey:@"email"];
        if (email != nil && ![email isEqual:[NSNull null]]) {
            parameters.email = email;
        }
        
        NSString *link = [dictionary objectForKey:@"link"];
        if (link != nil && ![link isEqual:[NSNull null]]) {
            parameters.website = link;
        }
        
    
        NSString *avatar = [NSString stringWithFormat:@"https://graph.facebook.com/%@/picture&type=large", [dictionary objectForKey:@"id"]];
        parameters.tempImageURL = avatar;
        
        [[STAuth sharedInstance] facebookSignupWithToken:[[[STFacebook sharedInstance] facebook] accessToken] params:parameters];
        [parameters release];
        
    } else if (_signupType == SignupWelcomeTypeEmail) {
        
        [[STAuth sharedInstance] updateStampWithPrimaryColor:primaryColor secondary:secondaryColor completion:^(NSError *error) {
            
            if (self.avatarTempPath) {
                [[STAuth sharedInstance] updateProfileImageWithPath:self.avatarTempPath completion:^(NSError *error) {  
                    if (self.avatarImage) {
                        [STStampedAPI sharedInstance].currentUserImage = self.avatarImage;
                    }
                    FindFriendsViewController *controller = [[FindFriendsViewController alloc] init];
                    controller.navigationItem.hidesBackButton = YES;
                    [self.navigationController pushViewController:controller animated:YES];
                    [controller release];
                }];
            } else {
                FindFriendsViewController *controller = [[FindFriendsViewController alloc] init];
                controller.navigationItem.hidesBackButton = YES;
                [self.navigationController pushViewController:controller animated:YES];
                [controller release];
            }
            
        }];
        
    }
    
}

- (void)cancel:(id)sender {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - UITableViewDataSource

- (CGFloat)tableView:(UITableView*)tableView heightForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    return 60.0f;
    
}

- (NSInteger)tableView:(UITableView*)tableView numberOfRowsInSection:(NSInteger)section {
    return 1;
}

- (UITableViewCell*)tableView:(UITableView*)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath {
    
    static NSString *CellIdentifier = @"CellIdentifier";

    if (_signupType == SignupWelcomeTypeEmail) {
        
        SignupCameraTableCell *cell = [tableView dequeueReusableCellWithIdentifier:CellIdentifier];
        if (cell == nil) {
            cell = [[[SignupCameraTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
            cell.delegate = (id<SignupCameraCellDelegate>)self;
        }
        
        cell.titleLabel.text = @"1. Add a profile picture";        
        return cell;
        
    }
    
    
    STTextFieldTableCell *cell = (STTextFieldTableCell*)[tableView dequeueReusableCellWithIdentifier:CellIdentifier];
    if (cell == nil) {
       
        cell = [[[STTextFieldTableCell alloc] initWithStyle:UITableViewCellStyleDefault reuseIdentifier:CellIdentifier] autorelease];
        cell.textField.delegate = (id<UITextFieldDelegate>)self;
        cell.textField.returnKeyType = UIReturnKeyDone;
        cell.textField.autocapitalizationType = UITextAutocapitalizationTypeNone;
        cell.textField.autocorrectionType = UITextAutocorrectionTypeNo;
        
        if (_signupType == SignupWelcomeTypeTwitter) {
            
            cell.textField.text = [[STTwitter sharedInstance] twitterUsername];
            
        } else if (_signupType == SignupWelcomeTypeFacebook) {

//            NSDictionary *dictionary = [[STFacebook sharedInstance] userData];
//            if ([dictionary objectForKey:@"username"]) {
//                cell.textField.text = [dictionary objectForKey:@"username"];
//            }
            
        }
        
    }
    cell.titleLabel.text = @"username";
  
    
    return cell;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForHeaderInSection:(NSInteger)section {
    
    if (_signupType == SignupWelcomeTypeEmail) {
        return 0.0f;
    }
    
    return 30.0f;
    
}

- (CGFloat)tableView:(UITableView*)tableView heightForFooterInSection:(NSInteger)section {
    
    return 30.0f;
    
}

- (UIView*)labelWithTitle:(NSString*)title {
    
    UIView *view = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.view.bounds.size.width, 30.0f)];
    
    UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
    label.backgroundColor = [UIColor clearColor];
    label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
    label.shadowColor = [UIColor whiteColor];
    label.shadowOffset = CGSizeMake(0.0f, 1.0f);
    label.font = [UIFont boldSystemFontOfSize:12];
    label.text = title;
    
    [label sizeToFit];
    CGRect frame = label.frame;
    frame.origin.x = 15.0f;
    frame.origin.y = floorf(((view.bounds.size.height-frame.size.height)/2) + 6.0f);
    label.frame = frame;
    [view addSubview:label];
    [label release];
    
    UIView *border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, view.bounds.size.width, 1.0f)];
    border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    border.backgroundColor = [[UIColor blackColor] colorWithAlphaComponent:0.05f];
    [view addSubview:border];
    [border release];
    
    border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, view.bounds.size.width, 1.0f)];
    border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
    border.backgroundColor = [[UIColor whiteColor] colorWithAlphaComponent:0.6f];
    [view addSubview:border];
    [border release];
    
    return [view autorelease];
    
}

- (UIView*)tableView:(UITableView*)tableView viewForHeaderInSection:(NSInteger)section {
    
    if (_signupType == SignupWelcomeTypeEmail) {
        return nil;
    }
    
    return [self labelWithTitle:@"Create your username"];
    
}

- (UIView*)tableView:(UITableView*)tableView viewForFooterInSection:(NSInteger)section {
    
    if (_signupType == SignupWelcomeTypeEmail) {
        return [self labelWithTitle:@"2. Choose your stamp color"];
    }
    
    return [self labelWithTitle:@"Choose your stamp color"];
    
}


#pragma mark - UIActionSheetDelegate

- (void)actionSheet:(UIActionSheet *)actionSheet clickedButtonAtIndex:(NSInteger)buttonIndex {
    if (buttonIndex == [actionSheet numberOfButtons]-1) return;
    
    UIImagePickerController *controller = [[UIImagePickerController alloc] init];
    controller.allowsEditing = YES;
    controller.delegate = (id<UIImagePickerControllerDelegate, UINavigationControllerDelegate>)self;
    
    if (buttonIndex == 0) {
        controller.sourceType = UIImagePickerControllerSourceTypePhotoLibrary;
    } else if (buttonIndex == 1) {
        controller.sourceType = UIImagePickerControllerSourceTypeCamera;
    }
    
    [self presentModalViewController:controller animated:YES];
    
}


#pragma mark - UIImagePickerControllerDelegate

- (void)imagePickerController:(UIImagePickerController *)picker didFinishPickingMediaWithInfo:(NSDictionary *)info {
    
    [picker dismissModalViewControllerAnimated:YES];    
    if ([info objectForKey:@"UIImagePickerControllerEditedImage"]) {
        UIImage *image = [info objectForKey:UIImagePickerControllerEditedImage];

        UIGraphicsBeginImageContext(CGSizeMake(500.0f, 500.0f));
        CGRect rect = [Util centeredAndBounded:image.size inFrame:CGRectMake(0, 0, 500, 500)];
        [image drawInRect:rect];
        image = UIGraphicsGetImageFromCurrentImageContext();
        UIGraphicsEndImageContext();
        
        if (self.tableView.tableHeaderView) {
            SocialSignupHeaderView *header = (SocialSignupHeaderView*)self.tableView.tableHeaderView;
            header.imageView.imageView.image = image;
        }
     
        [self.avatarUploader cancel];
        NSString *path = [NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES) objectAtIndex:0];
		path = [[path stringByAppendingPathComponent:[[NSProcessInfo processInfo] processName]] stringByAppendingPathComponent:@"UploadTemp"];
        [[NSFileManager defaultManager] createDirectoryAtPath:path withIntermediateDirectories:YES attributes:nil error:nil];
        path = [path stringByAppendingPathComponent:@"temp.jpg"];
        [[NSFileManager defaultManager] removeItemAtPath:path error:nil];
        [UIImageJPEGRepresentation(image, 0.85) writeToFile:path atomically:NO];
        self.avatarUploader.filePath = path;
        [self.avatarUploader startWithProgress:^(float progress) {
            
            SignupCameraTableCell *cell = (SignupCameraTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            if (cell) {
                [cell setProgress:progress];
            }
            
        } completion:^(NSString *path, BOOL finished) {
           
            SignupCameraTableCell *cell = (SignupCameraTableCell*)[self.tableView cellForRowAtIndexPath:[NSIndexPath indexPathForRow:0 inSection:0]];
            if (cell) {
                [cell setProgress:0.0f];
            }
            if (finished) {
                self.avatarImage = image;
            }
            
            self.avatarTempPath = path;
         
        }];
    
    }
    
}

- (void)imagePickerControllerDidCancel:(UIImagePickerController*)controller {
    [controller dismissModalViewControllerAnimated:YES];
}


#pragma mark - SignupCameraCellDelegate

- (void)signupCameraTableCellChoosePhoto:(SignupCameraTableCell*)cell {
    
    UIActionSheet *actionSheet = [[UIActionSheet alloc] initWithTitle:nil delegate:(id<UIActionSheetDelegate>)self cancelButtonTitle:nil destructiveButtonTitle:nil otherButtonTitles:nil];
    
    if ([UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypePhotoLibrary]) {
        [actionSheet addButtonWithTitle:@"Choose a Photo"];
    }
    
    if ([UIImagePickerController isSourceTypeAvailable:UIImagePickerControllerSourceTypeCamera]) {
        [actionSheet addButtonWithTitle:@"Take a Photo"];
    }
    
    [actionSheet addButtonWithTitle:NSLocalizedString(@"Cancel", nil)];
    actionSheet.cancelButtonIndex = [actionSheet numberOfButtons]-1;
    actionSheet.actionSheetStyle = UIActionSheetStyleBlackTranslucent;
    [actionSheet showInView:self.view];
    [actionSheet release];
    
}


#pragma mark - StampCustomizeViewControllerDelegate

- (void)stampCustomizeViewControllerCancelled:(StampCustomizeViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}

- (void)stampCustomizeViewController:(StampCustomizeViewController*)controller doneWithColors:(NSArray*)colors {
    NSMutableArray* fixedColors = [NSMutableArray array];
    for (UIColor* color in colors) {
        [fixedColors addObject:[UIColor stampedColorWithHex:[color insaneHexString]]];
    }
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(SocialSignupHeaderView*)self.tableView.tableHeaderView setStampColors:fixedColors];
    }
    
    if ([self.tableView.tableFooterView respondsToSelector:@selector(setSelectedColors:)]) {
        [(StampColorPickerView*)self.tableView.tableFooterView setSelectedColors:fixedColors];
    }
    
    [self dismissModalViewControllerAnimated:YES];

}


#pragma mark - StampColorPickerDelegate

- (void)stampColorPickerViewSelectedCustomize:(StampColorPickerView*)view {
    
    StampCustomizeViewController *controller = [[StampCustomizeViewController alloc] initWithColors:[view colors]];
    controller.delegate = (id<StampCustomizeViewControllerDelegate>)self;
    STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
    [self presentModalViewController:navController animated:YES];
    [navController release];
    [controller release];
    
}

- (void)stampColorPickerView:(StampColorPickerView*)view selectedColors:(NSArray*)colors {
    
    if ([self.tableView.tableHeaderView respondsToSelector:@selector(setStampColors:)]) {
        [(SocialSignupHeaderView*)self.tableView.tableHeaderView setStampColors:colors];
    }
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    [textField resignFirstResponder];
    return YES;
}


@end
