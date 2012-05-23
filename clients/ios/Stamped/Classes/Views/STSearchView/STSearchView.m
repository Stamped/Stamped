//
//  STSearchView.m
//  Stamped
//
//  Created by Devin Doty on 5/17/12.
//
//

#import "STSearchView.h"

@implementation STSearchView

@synthesize showCancelButton=_showCancelButton;
@synthesize delegate;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        _tap = [gesture retain];
        [gesture release];
        
        STSearchField *textField = [[STSearchField alloc] initWithFrame:CGRectMake(10, floorf((self.bounds.size.height-30.0f)/2), self.bounds.size.width-20.0f, 30)];
        [textField addTarget:self action:@selector(textFieldTextDidChange:) forControlEvents:UIControlEventEditingChanged];
        textField.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        textField.placeholder = @"Search";
        textField.delegate = (id<UITextFieldDelegate>)self;
        textField.enablesReturnKeyAutomatically = YES;
        textField.keyboardAppearance = UIKeyboardAppearanceDefault;
        [self addSubview:textField];
        _textField = textField;
        [textField release];
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        UIImage *image = [UIImage imageNamed:@"search_cancel_btn.png"];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:12];
        [button setTitleColor:[UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f] forState:UIControlStateNormal];
        button.frame = CGRectMake(CGRectGetMaxX(_textField.frame) + 10.0f, floorf((self.bounds.size.height-image.size.height)/2), 60.0f, image.size.height);
        button.titleLabel.shadowColor = [UIColor whiteColor];
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(cancel:) forControlEvents:UIControlEventTouchUpInside];
        [button setTitle:NSLocalizedString(@"Cancel", @"Cancel") forState:UIControlStateNormal];
        [self addSubview:button];
        button.hidden = YES;
        _cancelButton = button;
        
        UIImageView *corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_left.png"]];
        [self addSubview:corner];
        [corner release];
        _topLeftCorner = corner;
        
        corner = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"corner_top_right.png"]];
        [self addSubview:corner];
        [corner release];
        
        frame = corner.frame;
        frame.origin.x = (self.bounds.size.width - corner.frame.size.width);
        corner.frame = frame;
        _topRightCorner = corner;
        
        _topRightCorner.alpha = 0.0f;
        _topLeftCorner.alpha = 0.0f;
        
    }
    return self;
}

- (void)dealloc {
    [_tap release], _tap=nil;
    [super dealloc];
}

- (void)cancelSearch {
    
    [_textField resignFirstResponder];
    [_textField setText:nil];
    if ([(id)delegate respondsToSelector:@selector(stSearchViewDidCancel:)]) {
        [self.delegate stSearchViewDidCancel:self];
    }
    
}

- (void)setPlaceholderTitle:(NSString*)title {
    
    if (title) {
        _textField.placeholder = title;
    }
    
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
        
        _topRightCorner.alpha = show ? 1.0f : 0.0f;
        _topLeftCorner.alpha = show ? 1.0f : 0.0f;

        
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
    
    [_textField resignFirstResponder];
    [_textField setText:nil];
    if ([(id)delegate respondsToSelector:@selector(stSearchViewDidCancel:)]) {
        [self.delegate stSearchViewDidCancel:self];
    }
    
}

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    [_textField becomeFirstResponder];
    
}


#pragma mark - UIGestureRecognizerDelegate 

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    return ![_textField isFirstResponder] && !CGRectContainsPoint(_cancelButton.frame, [gestureRecognizer locationInView:self]);
    
}


#pragma mark - UITextFieldDelegate

- (BOOL)textFieldShouldBeginEditing:(UITextField *)textField {
    
    if ([(id)delegate respondsToSelector:@selector(stSearchViewDidBeginSearching:)]) {
        [self.delegate stSearchViewDidBeginSearching:self];
    }
    return YES;
}

- (BOOL)textFieldShouldEndEditing:(UITextField *)textField {
    
    if ([(id)delegate respondsToSelector:@selector(stSearchViewDidEndSearching:)]) {
        [self.delegate stSearchViewDidEndSearching:self];
    }
    return YES;
}

- (void)textFieldTextDidChange:(UITextField*)textField {
    
    if ([(id)delegate respondsToSelector:@selector(stSearchView:textDidChange:)]) {
        [self.delegate stSearchView:self textDidChange:textField.text];
    }

}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    
    if ([(id)delegate respondsToSelector:@selector(stSearchViewHitSearch:withText:)]) {
        [self.delegate stSearchViewHitSearch:self withText:textField.text];
    }

    return YES;
}


@end
