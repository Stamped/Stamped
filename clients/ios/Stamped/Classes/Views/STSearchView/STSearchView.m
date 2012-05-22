//
//  STSearchView.m
//  Stamped
//
//  Created by Devin Doty on 5/17/12.
//
//

#import "STSearchView.h"

@implementation STSearchView

@synthesize textField=_textField;
@synthesize showCancelButton=_showCancelButton;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        STSearchField *textField = [[STSearchField alloc] initWithFrame:CGRectMake(10, floorf((self.bounds.size.height-30.0f)/2), self.bounds.size.width-20.0f, 30)];
        textField.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        textField.placeholder = @"Search";
        textField.enablesReturnKeyAutomatically = NO;
        textField.keyboardAppearance = UIKeyboardAppearanceDefault;
        [self addSubview:textField];
        self.textField = textField;
        [textField release];
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        UIImage *image = [UIImage imageNamed:@"search_cancel_btn.png"];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f] forState:UIControlStateNormal];
        button.frame = CGRectMake(CGRectGetMaxX(self.textField.frame) + 10.0f, floorf((self.bounds.size.height-image.size.height)/2), 60.0f, image.size.height);
        button.titleLabel.shadowColor = [UIColor whiteColor];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(cancel:) forControlEvents:UIControlEventTouchUpInside];
        [button setTitle:NSLocalizedString(@"Cancel", @"Cancel") forState:UIControlStateNormal];
        [self addSubview:button];
        button.hidden = YES;
        _cancelButton = button;
        
    }
    return self;
}


#pragma mark - Setters

- (void)showCancel:(BOOL)show animated:(BOOL)animated {
    
    _cancelButton.hidden = NO;
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    
    __block UIView *textField = _textField;
    CGFloat width = self.bounds.size.width;
    
    [UIView animateWithDuration:0.2f delay:0.0f options:UIViewAnimationCurveEaseInOut animations:^{
        
        CGRect frame = _textField.frame;
        frame.size.width = floorf(width - (show ? 88.0f : 20.0f));
        textField.frame = frame;
        
        frame = _cancelButton.frame;
        frame.origin.x = floorf(CGRectGetMaxX(textField.frame) + 10.0f);
        _cancelButton.frame = frame;
        
    } completion:^(BOOL finished) {
        
        if (!show) {
            _cancelButton.hidden = YES;
        }
        
    }];
    
    [UIView setAnimationsEnabled:_enabled];
    
}

- (void)setShowCancelButton:(BOOL)showCancelButton {
    _showCancelButton = showCancelButton;
    [self showCancel:_showCancelButton animated:YES]; // default is animated
}


#pragma mark - Actions

- (void)cancel:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(stSearchViewDidCancel:)]) {
        [self.delegate stSearchViewDidCancel:self];
    }
    
}


@end
