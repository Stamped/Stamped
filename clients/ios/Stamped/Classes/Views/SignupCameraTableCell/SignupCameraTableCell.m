//
//  SignupCameraTableCell.m
//  Stamped
//
//  Created by Devin Doty on 6/6/12.
//
//

#import "SignupCameraTableCell.h"
#import "STProgressView.h"

@implementation SignupCameraTableCell
@synthesize delegate;
@synthesize progress=_progress;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
    if ((self = [super initWithStyle:style reuseIdentifier:reuseIdentifier])) {
        
        UIView *background = [[UIView alloc] initWithFrame:CGRectZero];
        self.backgroundView = background;
        [background release];
        
        UIImage *image = [UIImage imageNamed:@"sign_up_camera_btn.png"];
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin | UIViewAutoresizingFlexibleLeftMargin;
        button.frame = CGRectMake((self.bounds.size.width - (image.size.width+10.0f)), (self.bounds.size.height-image.size.height)/2, image.size.width, image.size.height);
        [button setImage:image forState:UIControlStateNormal];
        [self addSubview:button];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        
        UIFont *font = [UIFont boldSystemFontOfSize:12];
        UILabel *label = [[UILabel alloc] initWithFrame:CGRectMake(15.0f, floorf((self.bounds.size.height - font.lineHeight)/2), 0.0f, font.lineHeight)];
        label.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
        label.backgroundColor = [UIColor clearColor];
        label.textColor = [UIColor colorWithRed:0.600f green:0.600f blue:0.600f alpha:1.0f];
        label.shadowColor = [UIColor whiteColor];
        label.shadowOffset = CGSizeMake(0.0f, 1.0f);
        label.font = font;
        [self addSubview:label];
        self.titleLabel = label;
        [label release];
        
        UIView *border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, self.bounds.size.width, 1.0f)];
        border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        border.backgroundColor = [[UIColor blackColor] colorWithAlphaComponent:0.05f];
        [self addSubview:border];
        [border release];
        
        border = [[UIView alloc] initWithFrame:CGRectMake(0.0f, 1.0f, self.bounds.size.width, 1.0f)];
        border.autoresizingMask = UIViewAutoresizingFlexibleWidth;
        border.backgroundColor = [[UIColor whiteColor] colorWithAlphaComponent:0.6f];
        [self addSubview:border];
        [border release];
        
        
        
    }
    return self;
}

- (void)dealloc {
    self.titleLabel = nil;
    [super dealloc];
}

- (void)layoutSubviews {
    [super layoutSubviews];
    [self.titleLabel sizeToFit];
}


#pragma mark - Actions

- (void)buttonHit:(id)sender {
    
    if ([(id)delegate respondsToSelector:@selector(signupCameraTableCellChoosePhoto:)]) {
        [self.delegate signupCameraTableCellChoosePhoto:self];
    }
    
}


#pragma mark - Setters

- (void)setProgress:(CGFloat)progress {
    _progress = progress;
    
    if (_progress > 0.0f) {
        
        if (!_progressView) {
            self.titleLabel.hidden = YES;
            STProgressView *view = [[STProgressView alloc] initWithFrame:CGRectMake(15.0f, (self.bounds.size.height-5.0f)/2, 175.0f, 10.0f)];
            view.autoresizingMask = UIViewAutoresizingFlexibleTopMargin | UIViewAutoresizingFlexibleBottomMargin;
            [self addSubview:view];
            [view release];
            _progressView = view;
        }
        _progressView.progress = progress;
        
    } else {
        
        if (_progressView) {
            [_progressView removeFromSuperview], _progressView=nil;
        }
        self.titleLabel.hidden = NO;
        
    }
    
}


@end
