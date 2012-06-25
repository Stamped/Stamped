//
//  STCreateCommentView.m
//  Stamped
//
//  Created by Devin Doty on 6/18/12.
//
//

#import "STCreateCommentView.h"

#define KEYBOARD_HEIGHT 216.0f
#define DEFAULT_CALLOUT_HEIGHT 30
#define MAX_TEXTVIEW_HEIGHT ((460-64) - KEYBOARD_HEIGHT)
#define TEXT_VIEW_PLACEHOLDER @"Add a comment"

@interface STCreateCommentView ()
@property(nonatomic,retain) UIButton *sendButton;

- (void)showPlaceholder:(BOOL)show;
- (void)updateTextViewFrame:(UITextView*)textView;
@end

@implementation STCreateCommentView
@synthesize delegate;
@synthesize identifier;
@synthesize sendButton;

- (id)initWithFrame:(CGRect)frame {
    
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor clearColor];
        
        STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
        background.backgroundColor = [UIColor clearColor];
        background.contentMode = UIViewContentModeRedraw;
        background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
        [self addSubview:background];
        [background setDrawingHandler:^(CGContextRef ctx, CGRect rect) {
            
            drawGradient([UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:0.95f].CGColor, [UIColor colorWithRed:0.250f green:0.250f blue:0.250f alpha:0.95f].CGColor, UIGraphicsGetCurrentContext());

            [[UIColor colorWithRed:0.101f green:0.101f blue:0.101f alpha:1.0f] setStroke];
            CGContextMoveToPoint(ctx, 0.0f, rect.origin.y+.5);
            CGContextAddLineToPoint(ctx, self.bounds.size.width,  rect.origin.y+.5);
            CGContextStrokePath(ctx);
            
            [[UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:0.05f] setStroke];
            CGContextMoveToPoint(ctx, 0.0f, rect.origin.y+1.5);
            CGContextAddLineToPoint(ctx, self.bounds.size.width,  rect.origin.y+1.5);
            CGContextStrokePath(ctx);

            CGRect frame = CGRectInset(_textView.frame, -2, 1);
            frame.origin.y = floorf(frame.origin.y-2);
            frame.size.height =  floorf(frame.size.height+6);
            frame.size.width = rect.size.width - 68.0f;
            
            if (_textView.frame.size.height == (MAX_TEXTVIEW_HEIGHT+8)) {
                frame.size.height += 5;
            }
            
            UIImage *gutter = [UIImage imageNamed:@"comment_gutter_bg.png"];
            [[gutter stretchableImageWithLeftCapWidth:gutter.size.width/2 topCapHeight:gutter.size.height/2] drawInRect:frame];
            
        }];
        _backgroundView = background;
        [background release];
        
   		//  context text
		UITextView *textView = [[UITextView alloc] initWithFrame:CGRectMake(8.0f, floorf((frame.size.height/2) - (DEFAULT_CALLOUT_HEIGHT/2)), self.frame.size.width - 70.0f, DEFAULT_CALLOUT_HEIGHT)];
        textView.autoresizingMask = UIViewAutoresizingFlexibleRightMargin;
        textView.font = [UIFont systemFontOfSize:14];
		textView.keyboardAppearance = UIKeyboardAppearanceAlert;
		textView.scrollEnabled = NO;
        textView.delegate = (id<UITextViewDelegate>)self;
		textView.backgroundColor = [UIColor clearColor];
        textView.textColor = [UIColor stampedBlackColor];
		[self addSubview:textView];
		_textView = textView;
        [textView release];
        
        UIImage *image = [UIImage imageNamed:@"comment_send_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        [button addTarget:self action:@selector(send:) forControlEvents:UIControlEventTouchUpInside];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleLeftMargin;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setTitle:NSLocalizedString(@"Send", @"Send") forState:UIControlStateNormal];
        [button setTitleShadowColor:[UIColor colorWithWhite:0.0f alpha:.2] forState:UIControlStateNormal];
        [button setTitleColor:[UIColor colorWithWhite:1.0f alpha:1.0f] forState:UIControlStateNormal];
        button.titleLabel.shadowOffset = CGSizeMake(0.0f, -1.0f);
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [self addSubview:button];
        self.sendButton = button;
        button.frame = CGRectMake(self.bounds.size.width - 58.0f, floorf(((self.bounds.size.height-image.size.height)/2)+1.0f), 56.0f, image.size.height);
        
        [self showPlaceholder:![textView hasText]];
        
    }
    
    return self;
    
}

- (void)dealloc {
    
    
    NSLog(@"DEALLOC");
    
    _textView.delegate=nil;
    if (_textView && [_textView isFirstResponder]) {
        //[_textView resignFirstResponder];
    }
    
    _textView=nil;
    _activityView=nil;
    _keyboardButton=nil;
    self.identifier=nil;
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [super dealloc];
}


#pragma mark - Setters

- (void)showPlaceholder:(BOOL)show {
    
    if (show) {
        
        if (!_placeholder) {
            UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(10.0f, 10.0f, 200.0f, 20.0f)];
            label.autoresizingMask = UIViewAutoresizingFlexibleRightMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleTopMargin;
            label.font = [UIFont systemFontOfSize:13];
            label.textColor = [UIColor lightGrayColor];
            label.backgroundColor = [UIColor clearColor];
            [label setUserInteractionEnabled:NO];
            label.text = TEXT_VIEW_PLACEHOLDER;
            [label sizeToFit];
            [_textView addSubview:label];
            _placeholder = label;
        }
        
    } else {
        
        if (_placeholder) {
            [_placeholder removeFromSuperview], _placeholder=nil;
        }
        
    }
    
}

- (void)setText:(NSString*)text {
    
    [_textView setText:text];
    
}


#pragma mark - Getters

- (NSString*)text {
    
    if ([_textView hasText]) {
        return [_textView text];
    }
    return @"";
    
}


#pragma mark - Loading

- (void)setLoading:(BOOL)loading {
    _loading = loading;
    
    self.sendButton.hidden = _loading;
    
    if (_loading) {
        _textView.textColor = [UIColor stampedLightGrayColor];
        if (!_activityView) {
            
            UIActivityIndicatorView *view = [[UIActivityIndicatorView alloc] initWithActivityIndicatorStyle:UIActivityIndicatorViewStyleWhite];
            view.layer.position = self.sendButton.layer.position;
            view.autoresizingMask = UIViewAutoresizingFlexibleLeftMargin | UIViewAutoresizingFlexibleTopMargin;
            [self addSubview:view];
            [view startAnimating];
            _activityView = view;
            [view release];

        }
        
        [self showPlaceholder:NO];
        
    } else {
        _textView.textColor = [UIColor stampedBlackColor];
        if (_activityView) {
            [_activityView removeFromSuperview];
            _activityView=nil;
        }
        [self showPlaceholder:![_textView hasText]];
        
    }
    
    [_backgroundView setNeedsDisplay];

}


#pragma mark - Keyboard Notifications

- (void)keyboardWillShow:(NSDictionary*)userInfo {
    
    CGRect keyboardFrame = [[userInfo objectForKey:UIKeyboardFrameEndUserInfoKey] CGRectValue];
    CGFloat duration = [[userInfo objectForKey:UIKeyboardAnimationDurationUserInfoKey] floatValue];
    [UIView beginAnimations:nil context:NULL];
    [UIView setAnimationDuration:duration];
    CGRect frame = self.frame;
    frame.origin.y = floorf(self.superview.bounds.size.height - (keyboardFrame.size.height+self.bounds.size.height));
    self.frame = frame;    
    [UIView commitAnimations];
    
    if (_textView) {
        frame = _textView.frame;
        frame.size.width = self.bounds.size.width - 70.0f;
        _textView.frame = frame;
    }
    
}

- (void)keyboardWillHide:(NSDictionary*)userInfo {
    
    CGRect frame = self.frame;
    frame.origin.y = floorf(self.superview.frame.size.height - frame.size.height);    
    if (CGRectEqualToRect(frame, self.frame)) {
        return;
    }
    
    __block STCreateCommentView *selfRef = self;
    CGFloat duration = [[userInfo objectForKey:UIKeyboardAnimationDurationUserInfoKey] floatValue];
    [UIView animateWithDuration:duration animations:^{
        
        CGRect  frame = selfRef.frame;
        frame.origin.y = floorf(selfRef.superview.frame.size.height);
        selfRef.frame = frame;
        
        if (_textView) {
            frame = _textView.frame;
            frame.origin.x = 8.0f;
            frame.size.width = self.bounds.size.width - 70.0f;
            _textView.frame = frame;
        }
        
    }];
    
}


#pragma mark - Actions

- (void)send:(id)sender {
    if (_loading) return;
    if (![_textView hasText]) return;
    
    [self setLoading:YES];
    [[STStampedAPI sharedInstance] createCommentForStampID:self.identifier withBlurb:_textView.text andCallback:^(id<STComment> comment, NSError *error, STCancellation *cancellation) {
        
        [self setLoading:NO];
        
        if (comment && !error) {
            
            if ([(id)delegate respondsToSelector:@selector(stCreateCommentView:addedComment:)]) {
                [self.delegate stCreateCommentView:self addedComment:comment];
            }
            
        } else {
            [Util warnWithMessage:@"Comment creation failed!" andBlock:nil];
        }
                                              
    }];
    
    [self updateTextViewFrame:_textView];
    _textStore = _textView.text;
    //_textView.text = @"";
    
    
}

- (void)showAnimated:(BOOL)animated {
    
    if (_textView) {
        BOOL _enabled = [UIView areAnimationsEnabled];
        [UIView setAnimationsEnabled:animated];
        [_textView becomeFirstResponder];
        [UIView setAnimationsEnabled:_enabled];
    }
    
}

- (void)killKeyboard {
    
    if (_textView && [_textView isFirstResponder]) {
        [_textView resignFirstResponder];
    }
}


#pragma mark - UITextViewDelegate

- (BOOL)textView:(UITextView *)textView shouldChangeTextInRange:(NSRange)range replacementText:(NSString *)text {
    if (_loading) {
        return NO;
    }
    return YES;
}

- (void)updateTextViewFrame:(UITextView*)textView {
    
    if(textView.contentSize.height >= MAX_TEXTVIEW_HEIGHT){
        
        if (textView.frame.size.height != (MAX_TEXTVIEW_HEIGHT+8)) {
            
            textView.frame = CGRectMake(textView.frame.origin.x, textView.frame.origin.y, textView.frame.size.width, MAX_TEXTVIEW_HEIGHT+4);
            CGFloat height = floorf(textView.frame.size.height + 16);           
            self.frame = CGRectMake(self.frame.origin.x, self.superview.frame.size.height - (KEYBOARD_HEIGHT+height), self.frame.size.width, height);
            textView.scrollEnabled = YES;
            [textView flashScrollIndicators];  
            
        }
        
    } else {
        
        CGFloat height = ![textView hasText] ? DEFAULT_CALLOUT_HEIGHT : floorf(textView.contentSize.height)-4;
        textView.frame = CGRectMake(textView.frame.origin.x, textView.frame.origin.y, textView.frame.size.width, height);
        textView.scrollEnabled = NO;   
        textView.contentOffset = CGPointMake(0.0f, 2.0f);
        height = floorf(height+14);
        self.frame = CGRectMake(self.frame.origin.x, self.superview.frame.size.height - (KEYBOARD_HEIGHT+height), self.frame.size.width, height);
        
    }
    
	[self setNeedsDisplay];
    
}

- (void)textViewDidBeginEditing:(UITextView *)textView {  
    _visible=YES;
    textView.contentOffset = CGPointMake(0.0f, 2.0f);
    [self showPlaceholder:![textView hasText]];
    
    if ([(id)delegate respondsToSelector:@selector(stCreateCommentViewWillBeginEditing:)]) {
        [self.delegate stCreateCommentViewWillBeginEditing:self];
    }
    
}

- (void)textViewDidChange:(UITextView *)textView {
    
    [self updateTextViewFrame:textView];
    [self showPlaceholder:![textView hasText]];

}

- (void)textViewDidEndEditing:(UITextView *)textView {
    [self showPlaceholder:![textView hasText]];
    
    if ([(id)delegate respondsToSelector:@selector(stCreateCommentViewWillEndEditing:)]) {
        [self.delegate stCreateCommentViewWillEndEditing:self];
    }
    
}

- (BOOL)textViewShouldEndEditing:(UITextView *)textView {
    _visible=NO;
    return YES;
}


#pragma mark - ScrollViewDelegate

- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
	
	//  work around for textView scrolling when set to firstResponder
	if (!scrollView.scrollEnabled && scrollView.contentOffset.y > -20) {
		scrollView.contentOffset = CGPointMake(0.0f, 2.0f);
	}
    
}


@end
