//
//  CreditHeaderView.m
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import "CreditHeaderView.h"
#import "CreditBubbleCell.h"

#define kCellGapWidth 2.0f
#define kCellGapHeight 0.0f
#define kMinTextFieldWidth 120.0f
#define kFrameInset 10.0f
#define kCellHeight 28

#define kBlankTextFieldText  @"\u200B"


@implementation CreditHeaderView
@synthesize delegate;
@synthesize dataSource;
@synthesize editing=_editing;
@synthesize deleting=_deleting;

- (id)initWithFrame:(CGRect)frame {
    if ((self = [super initWithFrame:frame])) {
        
        self.backgroundColor = [UIColor whiteColor];
        
        _cells = [[NSMutableArray alloc] init];

        UIImageView *imageView = [[UIImageView alloc] initWithImage:[UIImage imageNamed:@"credit_picker_header_icon.png"]];
        [self addSubview:imageView];
        
        CGRect frame = imageView.frame;
        frame.origin.x = 10.0f;
        frame.origin.y = (self.bounds.size.height-frame.size.height)/2;
        imageView.frame = frame;
        [imageView release];

        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(floorf(CGRectGetMaxX(frame) + 4.0f), floorf(CGRectGetMinY(frame) + 2.0f), 0.0f, 0.0f)];
        label.font = [UIFont systemFontOfSize:12];
        label.textColor = [UIColor colorWithWhite:0.6f alpha:1.0f];
        label.backgroundColor = self.backgroundColor;
        label.text = @"Credit to";
        [self addSubview:label];
        _titleLabel = label;
        [label release];
        
        UIFont *font = [UIFont systemFontOfSize:12];
        UITextField *textField = [[UITextField alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 100.0f, font.lineHeight)];
        [textField addTarget:self action:@selector(textFieldTextDidChage:) forControlEvents:UIControlEventEditingChanged];
        textField.delegate = (id<UITextFieldDelegate>)self;
        textField.font = font;
        textField.returnKeyType = UIReturnKeyDone;
        textField.textColor = [UIColor colorWithWhite:0.149f alpha:1.0f];
        textField.backgroundColor = [UIColor whiteColor];
        [self addSubview:textField];
        [textField release];
        _textField = textField;
        _textField.hidden = YES;
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        [gesture release];
        
        UIView *border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, self.bounds.size.height, self.bounds.size.width, 1.0f)];
        border.backgroundColor = [UIColor whiteColor];
        border.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleWidth;
        [self addSubview:border];
        [border release];
    
    }
    return self;
}

- (void)dealloc {
    [_cells release], _cells=nil;
    [super dealloc];
}


#pragma mark - DataSource

- (void)reloadData {
    
    for (UIView *view in _cells) {
        [view removeFromSuperview];
    }
    [_cells removeAllObjects];
    
    NSInteger count = 0;
    if ([(id)dataSource respondsToSelector:@selector(creditHeaderViewNumberOfCells:)]) {
        count = [self.dataSource creditHeaderViewNumberOfCells:self];
    }
    
    if ([(id)dataSource respondsToSelector:@selector(creditHeaderView:cellForIndex:)]) {

        for (NSInteger i = 0; i < count; i++) {
            
            CreditBubbleCell *cell = [self.dataSource creditHeaderView:self cellForIndex:i];
            [cell addTarget:self action:@selector(cellSelected:) forControlEvents:UIControlEventTouchUpInside];
            [_cells addObject:cell];
            [self addSubview:cell];
            
        }
        
    }
  
    
    [self layoutCells:NO];
    
}


#pragma mark - Layout

- (void)layoutCells:(BOOL)animated {
    
    BOOL _enabled = [UIView areAnimationsEnabled];
    [UIView setAnimationsEnabled:animated];
    
    [UIView beginAnimations:nil context:NULL];
    [UIView setAnimationDuration:0.3f];
    
    CGFloat originX = CGRectGetMaxX(_titleLabel.frame) + 4.0f;
    CGFloat originY = 10.0f;
    CGRect frame;
    
    for (UIView *view in _cells) {
        
        [view sizeToFit];
        frame = view.frame;
        
        if ((originX + kCellGapWidth + frame.size.width) > (self.bounds.size.width - kFrameInset)) {
            originX = kFrameInset;
            originY += kCellHeight + kCellGapHeight;
        } 

        frame.origin = CGPointMake(originX, originY);
        originX += (frame.size.width + kCellGapWidth);
        view.frame = frame;
        
    }
    
    [UIView commitAnimations];
    [UIView setAnimationsEnabled:_enabled];

    
    if (_editing) {
    
        originX += kCellGapWidth;
        if (originX + kMinTextFieldWidth > self.bounds.size.width-kFrameInset) {
            originY += kCellHeight + kCellGapHeight;
            originX = kFrameInset;
        }
        
        frame = _textField.frame;
        frame.origin = CGPointMake(originX, originY);
        frame.origin.y = floorf(originY + ((34.0f-frame.size.height)/2));
        frame.size.width = floorf((self.bounds.size.width-kFrameInset) - originX);
        _textField.frame = frame;
    
    }
    
    originY += kCellHeight + kFrameInset;

    frame = self.frame;
    if (frame.size.height != originY) {
        frame.size.height = originY;
        self.frame = frame;
        if ([(id)delegate respondsToSelector:@selector(creditHeaderViewFrameChanged:)]) {
            [UIView animateWithDuration:0.3f animations:^{ 
                [self.delegate creditHeaderViewFrameChanged:self];
            }];
        }
    }
    
    if ([_textField isFirstResponder] && self.bounds.size.height > kCellHeight * 2) {
    
        if ([(id)delegate respondsToSelector:@selector(creditHeaderView:adjustOffset:)] && !_deleting) {
            [self.delegate creditHeaderView:self adjustOffset:CGPointMake(0.0f, self.bounds.size.height-30.0f)];
        }
        
    }
    
    
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [_titleLabel sizeToFit];
    [self layoutCells:NO];
}


#pragma mark - Actions

- (void)cellSelected:(CreditBubbleCell*)cell {
    
    [self setDeleting:YES];
    for (CreditBubbleCell *_cell in _cells) {
        
        if (cell != _cell) {
            _cell.selected = NO;
        }
        
    }    
    [cell setSelected:YES];
    _selectedCell = cell;
    
}


#pragma mark - Setters

- (void)setupWithItems:(NSArray*)items {
    
    
    
}

- (void)setDeleting:(BOOL)deleting {
    _deleting = deleting;
    
    if (_deleting) {
        
        if (!_tempTextField) {
            UITextField *textField = [[UITextField alloc] initWithFrame:CGRectZero];
            textField.delegate = (id<UITextFieldDelegate>)self;
            textField.returnKeyType = UIReturnKeyDone;
            [self addSubview:textField];
            _tempTextField = textField;
            [_tempTextField becomeFirstResponder];
        }
        _tempTextField.text = @" ";
        _textField.hidden = YES;
        
    } else {
        
        if (_editing) {
            _textField.hidden = NO;
            if (![_textField isFirstResponder]) {
                [_textField becomeFirstResponder];
            }
        }
        
        if (_tempTextField) {
            [_tempTextField removeFromSuperview], _tempTextField=nil;
        }
        if (_selectedCell) {
            [(id)_selectedCell setSelected:NO];
            _selectedCell = nil;
        }
        
    }
    
 
    
}

- (void)setEditing:(BOOL)editing {
    if(_editing == editing) return;
    
    _editing = editing;
    [self layoutCells:YES];
    _textField.hidden = !_editing;
    _textField.text = @"";
    
    if (_editing) {
        if ([(id)delegate respondsToSelector:@selector(creditHeaderViewDidBeginEditing:)]) {
            [self.delegate creditHeaderViewDidBeginEditing:self];
        }
    } else {
        if ([(id)delegate respondsToSelector:@selector(creditHeaderViewDidEndEditing:)]) {
            [self.delegate creditHeaderViewDidEndEditing:self];
        }
    }
    
}


#pragma mark - Gesture Actions

- (void)tapped:(UITapGestureRecognizer*)gesture {
    
    _textField.hidden = NO;
    if (![_textField isFirstResponder]) {
        [_textField becomeFirstResponder];
    }
    
}

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    
    CGPoint pos = [gestureRecognizer locationInView:self];
    for (UIView *view in _cells) {
        if (CGRectContainsPoint(view.frame, pos)) {
            return NO;
        }
    }
    
    return YES;
    
    
    
    if (_deleting) {
        
    
        
    }
    
    return !_editing;
}


#pragma mark - UITextFieldDelegate

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {

    if (textField == _tempTextField) {

        if (_selectedCell) {

            if ([(id)delegate respondsToSelector:@selector(creditHeaderView:willDeleteCell:)]) {
                [self.delegate creditHeaderView:self willDeleteCell:(id)_selectedCell];
            }
            
            // delete key hit with cell selected
            [_selectedCell removeFromSuperview];
            [_cells removeObject:_selectedCell];
            _selectedCell = nil;
            [self layoutCells:YES];
            [self setDeleting:NO];
            
            return NO;
            
        }
    } else {
        
        
        
    }
    
    return YES;

}

- (void)textFieldDidBeginEditing:(UITextField *)textField {
    if (_tempTextField == textField) return;
    self.editing = YES;
    [self setDeleting:NO];
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
    if (_tempTextField == textField || _deleting) return;
    self.editing = NO;
}

- (void)textFieldTextDidChage:(UITextField*)textField {
    
    if ([(id)delegate respondsToSelector:@selector(creditHeaderView:textChanged:)]) {
        [self.delegate creditHeaderView:self textChanged:textField.text];
    }
    
    if (textField.text.length == 0 && ![textField.text isEqualToString:kBlankTextFieldText]) {
        textField.text = kBlankTextFieldText;
    }
    
    
}

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    [self setDeleting:NO];
    [_textField resignFirstResponder];
    return YES;
}



@end
