//
//  CreateEditView.h
//  Stamped
//
//  Created by Devin Doty on 6/14/12.
//
//

#import <UIKit/UIKit.h>
#import "STUploadingImageView.h"

typedef enum {
    CreateEditKeyboardTypeText = 0,
    CreateEditKeyboardTypePhoto,
} CreateEditKeyboardType;

@class STAvatarView, CreateExpandedCaptureMenu, CreateExpandedToolBar, STUploadingImageView, CreateCreditToolbar;
@protocol CreateEditViewDelegate, CreateEditViewDataSource;
@interface CreateEditView : UIView {
    UIButton *_commentButton;
    UIButton *_captureButton;
}

@property(nonatomic,assign) id <CreateEditViewDelegate, UIScrollViewDelegate> delegate;
@property(nonatomic,assign) id <CreateEditViewDataSource> dataSource;

@property(nonatomic,retain) STAvatarView *avatarView;
@property(nonatomic,retain) UITextView *textView;
@property(nonatomic,retain) UIScrollView *scrollView;
@property(nonatomic,retain) STUploadingImageView *imageView;
@property(nonatomic,retain) CreateCreditToolbar *creditToolbar;
@property(nonatomic,retain) UILabel *textViewPlaceholder;

@property(nonatomic,assign) CreateEditKeyboardType keyboardType; // default CreateEditKeyboardTypeText
@property(nonatomic,assign) BOOL editing; // default NO

@property(nonatomic,retain) CreateExpandedCaptureMenu *menuView;
@property(nonatomic,retain) CreateExpandedToolBar *toolbar;

@property(nonatomic,retain) UITapGestureRecognizer *tapGesture;

- (void)layoutScrollView;
- (void)setupWithCreditUsernames:(NSArray*)usernames;

@end

@protocol CreateEditViewDelegate
- (void)createEditViewSelectedCreditPicker:(CreateEditView*)view;
- (void)createEditView:(CreateEditView*)view addPhotoWithSourceType:(UIImagePickerControllerSourceType)source;
@end
@protocol CreateEditViewDataSource
- (UIView*)createEditViewSuperview:(CreateEditView*)view;
@end