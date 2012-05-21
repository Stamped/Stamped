//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import <Twitter/Twitter.h>

#import "AccountManager.h"
#import "Entity.h"
#import "EntityDetailViewController.h"
#import "Stamp.h"
#import "User.h"
#import "Util.h"
#import "STSynchronousWrapper.h"
#import "STEntityDetailFactory.h"
#import "STScrollViewContainer.h"
#import "STStampedActions.h"
#import "STActionManager.h"
#import "STStampDetailHeaderView.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import "STStampedAPI.h"
#import "STStampDetailCommentsView.h"
#import "STToolbarView.h"
#import "STLikeButton.h"
#import "STTodoButton.h"
#import "STStampButton.h"
#import "STStampedAPI.h"
#import "STButton.h"
#import "TTTAttributedLabel.h"
#import "STCommentButton.h"
#import "STShareButton.h"
#import "STDetailActionView.h"


@interface STStampDetailViewController () <UIActionSheetDelegate, UITextViewDelegate>

@property (nonatomic, readwrite, retain) id<STStamp> stamp;

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail;
- (void)_deleteStampButtonPressed:(id)caller;
- (void)commentButtonPressed;

@property (nonatomic, readonly, retain) STStampDetailHeaderView* headerView;
@property (nonatomic, readonly, retain) STStampDetailCommentsView* commentsView;
@property (nonatomic, readwrite, retain) STCancellation* entityDetailCancellation;
@property (nonatomic, readonly, retain) UIView* addCommentView;
@property (nonatomic, readonly, retain) UITextView* commentTextView;
@property (nonatomic, readonly, retain) UIActivityIndicatorView* commentActivityView;

@end


@implementation STStampDetailViewController

@synthesize headerView = _headerView;
@synthesize commentsView = _commentsView;
@synthesize stamp = _stamp;
@synthesize toolbar = _toolbar;
@synthesize entityDetailCancellation = entityDetailCancellation_;
@synthesize addCommentView = addCommentView_;
@synthesize commentTextView = commentTextView_;
@synthesize commentActivityView = commentActivityView_;

- (id)initWithStamp:(id<STStamp>)stamp {
  id<STStamp> cachedStamp = [[STStampedAPI sharedInstance] cachedStampForStampID:stamp.stampID];
  if (cachedStamp) {
    stamp = cachedStamp;
  }
  self = [super init];
  if (self) {
    _stamp = [stamp retain];
  }
  return self;
}

- (void)dealloc {
  [_headerView release];
  [_commentsView release];
  [_stamp release];
  [_toolbar release];
  [entityDetailCancellation_ release];
  [addCommentView_ release];
  [commentTextView_ release];
  [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    CGFloat addCommentBorderWidth = 1;
    addCommentView_ = [[UIView alloc] initWithFrame:CGRectMake(-addCommentBorderWidth, -300, self.scrollView.frame.size.width + 2 * addCommentBorderWidth, 0)];
    addCommentView_.backgroundColor = [UIColor whiteColor];
    addCommentView_.layer.shadowOpacity = .4;
    addCommentView_.layer.shadowColor = [UIColor blackColor].CGColor;
    addCommentView_.layer.shadowRadius = 3;
    addCommentView_.layer.shadowOffset = CGSizeMake(0, -2);
    addCommentView_.layer.borderWidth = addCommentBorderWidth;
    addCommentView_.layer.borderColor = [UIColor colorWithWhite:229/255.0 alpha:1].CGColor;
    UIView* userImage = [Util profileImageViewForUser:self.stamp.user withSize:STProfileImageSize31];
    [Util reframeView:userImage withDeltas:CGRectMake(15, 9, 0, 0)];
    [addCommentView_ addSubview:userImage];
    
    commentTextView_ = [[UITextView alloc] initWithFrame:CGRectMake(58, 9, 250, 31)];
    commentTextView_.font = [UIFont fontWithName:@"Helvetica" size:14];
    commentTextView_.layer.borderColor = [UIColor colorWithWhite:230/255.0 alpha:1].CGColor;
    commentTextView_.layer.borderWidth = 1;
    commentTextView_.layer.cornerRadius = 2;
    commentTextView_.autocorrectionType = UITextAutocorrectionTypeYes;
    commentTextView_.returnKeyType = UIReturnKeySend;
    commentTextView_.keyboardAppearance = UIKeyboardAppearanceAlert;
    commentTextView_.delegate = self;
    commentTextView_.enablesReturnKeyAutomatically = YES;
    [addCommentView_ addSubview:commentTextView_];
    
    commentActivityView_ = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleGray];
    commentActivityView_.backgroundColor = [UIColor colorWithWhite:1 alpha:.6];
    commentActivityView_.hidden = YES;
    [self.addCommentView addSubview:commentActivityView_];
    
    addCommentView_.hidden = YES;
    [self.view addSubview:addCommentView_];
    
    UIBarButtonItem* backButton = [[[UIBarButtonItem alloc] initWithTitle:[Util truncateTitleForBackButton:self.stamp.entity.title]
                                                                    style:UIBarButtonItemStyleBordered
                                                                   target:nil
                                                                   action:nil] autorelease];
    [[self navigationItem] setBackBarButtonItem:backButton];
    
    _headerView = [[STStampDetailHeaderView alloc] initWithStamp:self.stamp];
    [self.scrollView appendChildView:_headerView];
    for (NSInteger i = 0; i < self.stamp.contents.count; i++) {
        _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp 
                                                                   index:i 
                                                                   style:STStampDetailCommentsViewStyleNormal 
                                                             andDelegate:self.scrollView];
        [self.scrollView appendChildView:_commentsView];
    }
    
    if ([AccountManager.sharedManager.currentUser.screenName isEqualToString:self.stamp.user.screenName]) {
        UIBarButtonItem* rightButton = [[[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                         style:UIBarButtonItemStylePlain
                                                                        target:self
                                                                        action:@selector(_deleteStampButtonPressed:)] autorelease];
        self.navigationItem.rightBarButtonItem = rightButton;
    }
    //[toolbar packViews:views];
    
    STDetailActionView *actionView = [[STDetailActionView alloc] initWithStamp:self.stamp delegate:self];
    [self.view addSubview:actionView];
    [actionView release];
        
    self.entityDetailCancellation = [[STStampedAPI sharedInstance] entityDetailForEntityID:self.stamp.entity.entityID andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
        
        STSynchronousWrapper* wrapper = [STSynchronousWrapper wrapperForStampDetail:detail withFrame:CGRectMake(0, 0, 320, 200) stamp:self.stamp delegate:self.scrollView];
        [self.scrollView appendChildView:wrapper];
        self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width, self.scrollView.contentSize.height);
        UIView* padding = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 60)] autorelease];
        [self.scrollView appendChildView:padding];
        
    }];
  
}

- (void)viewDidUnload {
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    //[self setUpToolbar];
    [_headerView setNeedsDisplay];
    NSLog(@"viewWillAppear");
}

- (void)viewWillDisappear:(BOOL)animated {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    if ([self.commentTextView isFirstResponder]) {
        [self.commentTextView resignFirstResponder];
    }
    [[STActionManager sharedActionManager] setStampContext:nil];
    [super viewWillDisappear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
    if ([self.commentTextView isFirstResponder]) {
        [self.commentTextView resignFirstResponder];
    }
    [super viewDidAppear:animated];
    [[STActionManager sharedActionManager] setStampContext:self.stamp];
    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(keyboardWasShown:)
                                                 name:UIKeyboardDidShowNotification 
                                               object:nil];
    [[NSNotificationCenter defaultCenter] addObserver:self 
                                             selector:@selector(keyboardWasHidden:)
                                                 name:UIKeyboardDidHideNotification
                                               object:nil];
}

- (void)cancelPendingRequests {
  [self.entityDetailCancellation cancel];
}

- (void)changeFirstResponder {
  //[self.dummyTextField.inputAccessoryView becomeFirstResponder];
}

- (void)_deleteStampButtonPressed:(id)caller {
  [Util confirmWithMessage:@"Are you sure?" action:@"Delete" destructive:YES withBlock:^(BOOL confirmed) {
    if (confirmed) {
      STActionContext* context = [STActionContext contextWithCompletionBlock:^(id success, NSError *error) {
        if (!error) {
          [[Util sharedNavigationController] popViewControllerAnimated:YES];
        }
      }];
      id<STAction> action = [STStampedActions actionDeleteStamp:self.stamp.stampID withOutputContext:context];
      [[STActionManager sharedActionManager] didChooseAction:action withContext:context];    }
  }];
}

- (void)_didLoadEntityDetail:(id<STEntityDetail>)detail {
  CGFloat wrapperHeight = 200;
  CGRect wrapperFrame = CGRectMake(0, 0 , 320, wrapperHeight);
  STSynchronousWrapper* eDetailView = [STSynchronousWrapper wrapperForEntityDetail:detail
                                                                         withFrame:wrapperFrame 
                                                                          andStyle:@"StampDetail" 
                                                                          delegate:self.scrollView];
  [self.scrollView appendChildView:eDetailView];
}

- (UIView *)toolbar {
  return _toolbar;
}


#pragma mark - Actions

- (void)handleEntityTap:(id)sender {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)commentButtonPressed {
  [self.commentTextView becomeFirstResponder];
}


#pragma mark - STActionViewDelegate

- (void)stActionView:(STDetailActionView*)view itemSelectedAtIndex:(NSInteger)index {
    
    
}


#pragma mark - Keyboard Notifications

- (void)keyboardWasShown:(NSNotification *)notification {
    CGSize keyboardSize = [[[notification userInfo] objectForKey:UIKeyboardFrameBeginUserInfoKey] CGRectValue].size;
    
    CGRect frame = self.addCommentView.frame;
    self.addCommentView.clipsToBounds = YES;
    frame.origin.y = self.view.frame.size.height - ( keyboardSize.height );
    CGFloat height = 51;
    frame.size.height = 0;
    self.addCommentView.frame = frame;
    self.addCommentView.hidden = NO;
    [UIView animateWithDuration:.25 animations:^{
        [Util reframeView:self.addCommentView withDeltas:CGRectMake(0, -height, 0, height)];
    }];
}

- (void)keyboardWasHidden:(NSNotification *)notification {
    CGRect frame = self.addCommentView.frame;
    frame.origin.y = -300;
    self.addCommentView.frame = frame;
    self.addCommentView.hidden = YES;
}


#pragma mark - UITextViewDelegate

- (BOOL)textView:(UITextView *)textView shouldChangeTextInRange:(NSRange)range replacementText:(NSString *)text {
  if (!self.commentActivityView.hidden) {
    return FALSE;
  }
  else {
    if ([text isEqualToString:@"\n"]) {
      self.commentActivityView.hidden = NO;
      self.commentActivityView.frame = CGRectMake(0, 0, self.addCommentView.frame.size.width, self.addCommentView.frame.size.height);
      [self.commentActivityView startAnimating];
      [[STStampedAPI sharedInstance] createCommentForStampID:self.stamp.stampID 
                                                   withBlurb:textView.text 
                                                 andCallback:^(id<STComment> comment, NSError *error, STCancellation *cancellation) {
                                                   [self.commentActivityView stopAnimating];
                                                   self.commentActivityView.hidden = YES;
                                                   if (comment && !error) {
                                                     self.addCommentView.hidden = YES;
                                                     textView.text = @"";
                                                     [textView resignFirstResponder];
                                                     [self reloadStampedData];
                                                   }
                                                   else {
                                                     [Util warnWithMessage:@"Comment creation failed!" andBlock:nil];
                                                   }
                                                 }];
      return FALSE;
    }
    return TRUE;
  }
}

- (void)textViewDidChange:(UITextView *)textView {
  CGFloat heightDelta = textView.contentSize.height - textView.frame.size.height;
  if (heightDelta > 0 && textView.frame.size.height + heightDelta < 70) {
    [UIView animateWithDuration:.25 animations:^{
      [Util reframeView:self.addCommentView withDeltas:CGRectMake(0, -heightDelta, 0, heightDelta)];
      [Util reframeView:self.commentTextView withDeltas:CGRectMake(0, 0, 0, heightDelta)];
    }];
  }
}

@end
