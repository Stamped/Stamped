//
//  STTextFieldTableCell.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "STTextFieldTableCell.h"

@implementation STTextFieldTableCell
@synthesize textField=_textField;
@synthesize titleLabel=_titleLabel;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {

        self.selectionStyle = UITableViewCellSelectionStyleNone;
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectZero];
        self.backgroundView = background;
        [background release];
        
        UIImage *image = [UIImage imageNamed:@"signup_text_field_bg.png"];
        UIImageView *imageView = [[UIImageView alloc] initWithImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0]];
        imageView.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        imageView.frame = CGRectMake(10.0f, 0.0f, floorf(self.bounds.size.width - 20.0f), image.size.height);
        [self addSubview:imageView];
        [imageView release];
        
        UIFont *font = [UIFont systemFontOfSize:13];
        UITextField *textField = [[UITextField alloc] initWithFrame:CGRectMake(20.0f, floorf((image.size.height-20.0f)/2), floorf(self.bounds.size.width - 40.0f), 20.0f)];
        textField.font = font;
        textField.textColor = [UIColor colorWithRed:0.149f green:0.149f blue:0.149f alpha:1.0f];
        textField.backgroundColor = [UIColor clearColor];
        textField.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        textField.clearButtonMode = UITextFieldViewModeWhileEditing;
        [self addSubview:textField];
        _textField = [textField retain];
        [textField release];
        
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
        label.userInteractionEnabled = NO;
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleRightMargin;
        label.backgroundColor = [UIColor clearColor];
        label.font = [UIFont systemFontOfSize:12];
        label.textColor = [UIColor colorWithRed:0.749f green:0.749f blue:0.749f alpha:1.0f];
        [imageView addSubview:label];
        _titleLabel = [label retain];
        [label release];
        
        UITapGestureRecognizer *gesture = [[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(tapped:)];
        gesture.delegate = (id<UIGestureRecognizerDelegate>)self;
        [self addGestureRecognizer:gesture];
        [gesture release];
        
    }
    return self;
}

- (void)dealloc {
    [_titleLabel release],_titleLabel=nil;
    [_textField release], _textField=nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    
    [self.titleLabel sizeToFit];
    CGRect frame = self.titleLabel.frame;
    
    if (self.titleLabel.textAlignment == UITextAlignmentRight) {
        frame.origin.x = 100 - frame.size.width;
    } else {
        frame.origin.x = 20.0f;
    }
    frame.origin.y = floorf((44.0f-frame.size.height)/2);
    self.titleLabel.frame = frame;
    
    frame = self.textField.frame;
    frame.origin.x = CGRectGetMaxX(self.titleLabel.frame) + 20.0f;
    frame.size.width = floorf(self.bounds.size.width - (frame.origin.x+30.0f));
    self.textField.frame = frame;
    
}

- (void)disable {

    self.userInteractionEnabled = NO;
    self.alpha = 0.6f;
    
}

- (void)enable {
    
    self.userInteractionEnabled = YES;
    self.alpha = 1.0f;
    
}


#pragma mark - Gesture

- (void)tapped:(UITapGestureRecognizer*)gesture {
    [self.textField becomeFirstResponder];    
}


#pragma mark - UIGestureRecognizerDelegate

- (BOOL)gestureRecognizerShouldBegin:(UIGestureRecognizer *)gestureRecognizer {
    return !CGRectContainsPoint(self.textField.frame, [gestureRecognizer locationInView:self]);
}


@end

