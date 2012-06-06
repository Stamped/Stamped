//
//  STStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailViewController.h"

#import <Twitter/Twitter.h>

#import "EntityDetailViewController.h"
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

@interface STStampDetailToolbar : UIView

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp;
- (void)toggleToolbar:(id)button;

@property (nonatomic, readonly, retain) NSArray* buttons;
@property (nonatomic, readwrite, assign) BOOL expanded;
@property (nonatomic, readonly, retain) UIView* expandButton;
@property (nonatomic, readonly, retain) UIView* buttonContainer;

@end

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
@property (nonatomic, readonly, retain) UIView* addCommentShading;

@end

@implementation STStampDetailToolbar

@synthesize buttons = buttons_;
@synthesize expanded = expanded_;
@synthesize expandButton = expandButton_;
@synthesize buttonContainer = buttonContainer_;

- (id)initWithParent:(UIView*)view controller:(STStampDetailViewController*)controller andStamp:(id<STStamp>)stamp {
    CGFloat xPadding = 5;
    CGFloat yPadding = 10;
    CGFloat height = 40;
    CGRect frame = CGRectMake(xPadding, view.frame.size.height - (height + yPadding), view.frame.size.width - (2 * xPadding), height);
    self = [super initWithFrame:frame];
    if (self) {
        expanded_ = YES;
        self.layer.cornerRadius = 5;
        self.layer.shadowOpacity = .3;
        self.layer.shadowRadius = 3;
        self.layer.shadowOffset = CGSizeMake(0, 2);
        self.layer.borderColor = [UIColor colorWithWhite:89.0/255 alpha:1].CGColor;
        self.layer.borderWidth = 1;
        [Util addGradientToLayer:self.layer 
                      withColors:[NSArray arrayWithObjects:
                                  [UIColor colorWithWhite:.4 alpha:.80],
                                  [UIColor colorWithWhite:.2 alpha:.85],
                                  nil] 
                        vertical:YES];
        UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more"]] autorelease];
        UIImageView* imageView2 = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"sDetailBar_btn_more_active"]] autorelease];
        expandButton_ = [[STButton alloc] initWithFrame:imageView.frame 
                                             normalView:imageView 
                                             activeView:imageView2 
                                                 target:self 
                                              andAction:@selector(toggleToolbar:)];
        [Util reframeView:expandButton_ withDeltas:CGRectMake(frame.size.width - (expandButton_.frame.size.width + 10), 10, 0, 0)];
        
        __block STStampDetailViewController* weakController = controller;
        STCommentButton* commentButton = [[[STCommentButton alloc] initWithCallback:^{
            [weakController commentButtonPressed];
        }] autorelease];
        
        buttons_ = [[NSMutableArray arrayWithObjects:
                     [[[STLikeButton alloc] initWithStamp:stamp] autorelease],
                     commentButton,
                     [[[STStampButton alloc] initWithStamp:stamp] autorelease],
                     [[[STTodoButton alloc] initWithStamp:stamp] autorelease],
                     [[[STShareButton alloc] initWithCallback:^{
            [Util executeOnMainThread:^{
                [Util warnWithMessage:@"No leaking Stamped 2.0!" andBlock:nil];
            }];
        }] autorelease],
                     nil] retain];
        CGFloat buttonSpacing = 60;
        buttonContainer_ = [[UIView alloc] initWithFrame:CGRectMake(0, -3, CGRectGetMinX(expandButton_.frame)+50, frame.size.height-7)];
        for (NSInteger i = 0; i < buttons_.count; i++) {
            UIView* button = [buttons_ objectAtIndex:i];
            [Util reframeView:button withDeltas:CGRectMake(-5 + (i * buttonSpacing), -4, 0, 0)];
            [buttonContainer_ addSubview:button];
        }
        buttonContainer_.clipsToBounds = NO;
        [self addSubview:buttonContainer_];
        self.clipsToBounds = YES;
        [Util reframeView:expandButton_ withDeltas:CGRectMake(3, -3, 0, 0)];
        [self addSubview:expandButton_];
        [self toggleToolbar:nil];
    }
    return self;
}

- (void)toggleToolbar:(id)notImportant {
    CGFloat delta = 155;
    CGFloat deltaSpacing = 15;
    CGFloat duration = .5;
    if (self.expanded) {
        [UIView animateWithDuration:duration animations:^{
            [Util reframeView:self withDeltas:CGRectMake(delta, 0, -delta, 0)];
            [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, -delta, 0)];
            [Util reframeView:self.expandButton withDeltas:CGRectMake(-delta, 0, 0, 0)];
            for (NSInteger i = 0; i < buttons_.count; i++) {
                UIView* button = [buttons_ objectAtIndex:i];
                [Util reframeView:button withDeltas:CGRectMake(i * -deltaSpacing, 0, 0, 0)];
                if (CGRectGetMaxX(button.frame) - 20 > self.buttonContainer.frame.size.width - 50) {
                    button.alpha = 0;
                }
            }
        }];
    }
    else {
        [UIView animateWithDuration:duration animations:^{
            [Util reframeView:self withDeltas:CGRectMake(-delta, 0, delta, 0)];
            [Util reframeView:self.buttonContainer withDeltas:CGRectMake(0, 0, delta, 0)];
            [Util reframeView:self.expandButton withDeltas:CGRectMake(delta, 0, 0, 0)];
            for (NSInteger i = 0; i < buttons_.count; i++) {
                UIView* button = [buttons_ objectAtIndex:i];
                [Util reframeView:button withDeltas:CGRectMake(i * deltaSpacing, 0, 0, 0)];
                button.alpha = 1;
            }
        }];
    }
    self.expanded = !self.expanded;
}

- (void)reloadStampedData {
    for (id view in self.buttonContainer.subviews) {
        if ([view respondsToSelector:@selector(reloadStampedData)]) {
            [view reloadStampedData]; 
        }
    }
}

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
@synthesize addCommentShading = _addCommentShading;

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

- (void)dealloc
{
    [_headerView release];
    [_commentsView release];
    [_stamp release];
    [_toolbar release];
    [entityDetailCancellation_ release];
    [addCommentView_ release];
    [commentTextView_ release];
    [_addCommentShading release];
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    _addCommentShading = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, self.view.frame.size.height)];
    _addCommentShading.backgroundColor = [UIColor colorWithWhite:0 alpha:.3];
    [_addCommentShading addGestureRecognizer:[[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(exitComment:)] autorelease]];
    _addCommentShading.userInteractionEnabled = NO;
    _addCommentShading.alpha = 0;
    [self.view addSubview:_addCommentShading];
    
    CGFloat addCommentBorderWidth = 1;
    addCommentView_ = [[UIView alloc] initWithFrame:CGRectMake(-addCommentBorderWidth, -300, self.scrollView.frame.size.width + 2 * addCommentBorderWidth, 0)];
    addCommentView_.backgroundColor = [UIColor whiteColor];
    addCommentView_.layer.shadowOpacity = .4;
    addCommentView_.layer.shadowColor = [UIColor blackColor].CGColor;
    addCommentView_.layer.shadowRadius = 3;
    addCommentView_.layer.shadowOffset = CGSizeMake(0, -2);
    addCommentView_.layer.borderWidth = addCommentBorderWidth;
    addCommentView_.layer.borderColor = [UIColor colorWithWhite:229/255.0 alpha:1].CGColor;
    UIView* userImage = [Util profileImageViewForUser:[STStampedAPI sharedInstance].currentUser withSize:STProfileImageSize31];
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
    _commentsView = [[STStampDetailCommentsView alloc] initWithStamp:self.stamp 
                                                         andDelegate:self.scrollView];
    [self.scrollView appendChildView:_commentsView];
    if ([STStampedAPI.sharedInstance.currentUser.screenName isEqualToString:self.stamp.user.screenName]) {
        UIBarButtonItem* rightButton = [[[UIBarButtonItem alloc] initWithTitle:@"Delete"
                                                                         style:UIBarButtonItemStylePlain
                                                                        target:self
                                                                        action:@selector(_deleteStampButtonPressed:)] autorelease];
        self.navigationItem.rightBarButtonItem = rightButton;
    }
    //[toolbar packViews:views];
    UIView* newToolbar = [[[STStampDetailToolbar alloc] initWithParent:self.view controller:self andStamp:self.stamp] autorelease];
    [self.view addSubview:newToolbar];
    
    self.entityDetailCancellation = [[STStampedAPI sharedInstance] entityDetailForEntityID:self.stamp.entity.entityID 
                                                                               andCallback:^(id<STEntityDetail> detail, NSError *error, STCancellation *cancellation) {
                                                                                   
                                                                                   STSynchronousWrapper* wrapper = [STSynchronousWrapper wrapperForStampDetail:detail withFrame:CGRectMake(0, 0, 320, 200) stamp:self.stamp delegate:self.scrollView];
                                                                                   [self.scrollView appendChildView:wrapper];
                                                                                   self.scrollView.contentSize = CGSizeMake(self.scrollView.contentSize.width, self.scrollView.contentSize.height);
                                                                                   UIView* padding = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 0, 60)] autorelease];
                                                                                   [self.scrollView appendChildView:padding];
                                                                               }];
    
    
}

- (void)viewDidUnload {
}

- (void)cancelPendingRequests {
    [self.entityDetailCancellation cancel];
}


- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    //[self setUpToolbar];
    [_headerView setNeedsDisplay];
    NSLog(@"viewWillAppear");
}

- (void)exitComment:(id)notImportant {
    if ([self.commentTextView isFirstResponder]) {
        [self.commentTextView resignFirstResponder];
    }
}

- (void)changeFirstResponder {
    //[self.dummyTextField.inputAccessoryView becomeFirstResponder];
}

- (void)keyboardWasShown:(NSNotification *)notification
{
    CGSize keyboardSize = [[[notification userInfo] objectForKey:UIKeyboardFrameBeginUserInfoKey] CGRectValue].size;
    
    CGRect frame = self.addCommentView.frame;
    self.addCommentView.clipsToBounds = YES;
    frame.origin.y = self.view.frame.size.height - ( keyboardSize.height );
    CGFloat height = 51;
    frame.size.height = 0;
    self.addCommentView.frame = frame;
    self.addCommentView.hidden = NO;
    self.addCommentView.alpha = 1;
    [UIView animateWithDuration:.25 animations:^{
        [Util reframeView:self.addCommentView withDeltas:CGRectMake(0, -height, 0, height)];
        _addCommentShading.alpha = 1;
        _addCommentShading.userInteractionEnabled = YES;
    }];
}

- (void)keyboardWasHidden:(NSNotification *)notification
{
    _addCommentShading.userInteractionEnabled = NO;
    CGRect frame = self.addCommentView.frame;
    frame.origin.y = self.view.frame.size.height;
    [UIView animateWithDuration:.3
                     animations:^{
                         self.addCommentView.frame = frame;
                         self.addCommentView.alpha = 0;
                         _addCommentShading.alpha = 0;
                     } completion:^(BOOL finished) {
                         
                         self.addCommentView.hidden = YES;
                     }];
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

- (void)viewWillDisappear:(BOOL)animated {
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    if ([self.commentTextView isFirstResponder]) {
        [self.commentTextView resignFirstResponder];
    }
    [[STActionManager sharedActionManager] setStampContext:nil];
    [super viewWillDisappear:animated];
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

- (void)handleEntityTap:(id)sender {
    STActionContext* context = [STActionContext context];
    id<STAction> action = [STStampedActions actionViewEntity:self.stamp.entity.entityID withOutputContext:context];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (UIView *)toolbar {
    return _toolbar;
}

- (void)commentButtonPressed {
    [self.commentTextView becomeFirstResponder];
}

- (BOOL)textView:(UITextView *)textView shouldChangeTextInRange:(NSRange)range replacementText:(NSString *)text
{
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